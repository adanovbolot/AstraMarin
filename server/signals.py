from datetime import date
from django.db.models import Sum
import os
import qrcode
from django.conf import settings
from server.models import Tickets, SalesReport, PointsSale
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.dispatch import receiver
from PIL import Image, ImageDraw, ImageFont
from django.core.files import File
import json


@receiver(post_save, sender=PointsSale)
def create_sales_report(sender, instance, created, **kwargs):
    if created:
        points_sale = instance
        report_date = points_sale.create_data
        operator = points_sale.operator
        points_sale_instance = PointsSale.objects.get(operator=operator)
        SalesReport.objects.create(operator=points_sale_instance, report_date=report_date)


@receiver(post_save, sender=Tickets)
def update_sales_report(sender, instance, created, **kwargs):
    ticket = instance
    points_sale = ticket.operator
    if points_sale.status == 'Открытая смена' and points_sale.create_data == date.today():
        try:
            sales_report = points_sale.sales_reports.get(report_date=date.today())
        except SalesReport.DoesNotExist:
            sales_report = SalesReport(operator=points_sale, report_date=date.today())
        total_adult_quantity = points_sale.tickets_points_sale.aggregate(total_adults=Sum('adult_quantity')).get(
            'total_adults', 0)
        total_child_quantity = points_sale.tickets_points_sale.aggregate(total_children=Sum('child_quantity')).get(
            'total_children', 0)
        total_amount_report = points_sale.tickets_points_sale.aggregate(total_amount=Sum('total_amount')).get(
            'total_amount', 0)
        sales_report.total_adult_quantity = total_adult_quantity
        sales_report.total_child_quantity = total_child_quantity
        sales_report.total_amount_report = total_amount_report
        sales_report.save()


@receiver(m2m_changed, sender=Tickets.price_types.through)
def handle_price_types_change(sender, instance, **kwargs):
    calculate_total_amount(instance)


@receiver(post_save, sender=Tickets)
def handle_ticket_save(sender, instance, **kwargs):
    post_save.disconnect(handle_ticket_save, sender=Tickets)
    calculate_total_amount(instance)
    generate_check(instance)
    post_save.connect(handle_ticket_save, sender=Tickets)


def calculate_total_amount(instance):
    adult_quantity = instance.adult_quantity or 0
    child_quantity = instance.child_quantity or 0
    price_types = instance.price_types.all()

    total_amount = 0
    for price_type in price_types:
        price = price_type.price.price
        if price_type.client_type == 'Ребенок':
            total_amount += price * child_quantity
        elif price_type.client_type == 'Взрослый':
            total_amount += price * adult_quantity

    instance.total_amount = total_amount
    instance.save()


def generate_check(instance):
    check_path = os.path.join(settings.MEDIA_ROOT, 'tickets', 'check')
    filename = f'check_{instance.pk}.png'
    os.makedirs(check_path, exist_ok=True)
    check_image = Image.new('RGB', (400, 900), (255, 255, 255))
    draw = ImageDraw.Draw(check_image)
    logo_path = os.path.join(settings.MEDIA_ROOT, 'images', 'логотип_Восход.png')
    logo_image = Image.open(logo_path)
    new_logo_width = 550
    new_logo_height = int((new_logo_width / logo_image.width) * logo_image.height)
    logo_image = logo_image.resize((new_logo_width, new_logo_height))
    logo_position = ((check_image.width - logo_image.width) // 2, 10)
    check_image.paste(logo_image, logo_position)
    text_font = ImageFont.truetype("arial.ttf", 13, encoding="unic")
    text_lines = [
        f"Кассир: {instance.operator}",
        f"билет действителен до: {instance.ticket_day}",
        f"\n",
        f'Время начало: {instance.ship.start_time}\n',
        f'Время окончания: {instance.ship.end_time}\n',
        f"\n",
        f"Судно: {instance.ship.ship}",
        f"Площадка: {instance.area.address}",
        f"Причал: {instance.ship.berths}",
        f"Количество взрослых: {instance.adult_quantity}",
        f"Количество детей: {instance.child_quantity}",
        f"Дата билета: {instance.created_at}",
        f"------------------------------------------------\n"
        f"Общая сумма: {instance.total_amount}",
        f"\n",
        str(instance),
    ]
    text_position = (
    (check_image.width - max([text_font.getsize(line)[0] for line in text_lines])) // 2, 100)
    text_spacing = 27
    for line in text_lines:
        draw.text(text_position, line, font=text_font, fill=(0, 0, 0))
        text_position = (text_position[0], text_position[1] + text_spacing)
    qr_size = 300
    qr_data = {
        'id': instance.pk,
        'operator': str(instance.operator),
        'ticket_day': str(instance.ticket_day),
        'ship_vessel': str(instance.ship),
        'ship_start_time': str(instance.ship.start_time),
        'ship_end_time': str(instance.ship.end_time),
        'total_amount': str(instance.total_amount),
        'area': str(instance.area),
        'created_at': str(instance.created_at),
        'bought': str(instance.bought),
        'ticket_has_expired': str(instance.ticket_has_expired),
        'adult_quantity': str(instance.adult_quantity),
        'child_quantity': str(instance.child_quantity),
    }
    qr_data_json = json.dumps(qr_data, ensure_ascii=False)
    qr_position = ((check_image.width - qr_size) // 2, check_image.height - qr_size - 70)
    qr_code = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=50,
        border=2,
    )
    qr_code.add_data(qr_data_json)
    qr_code.make(fit=True)
    qr_image = qr_code.make_image(fill_color="black", back_color="white")
    qr_image = qr_image.resize((qr_size, qr_size))
    check_image.paste(qr_image, qr_position)
    check_image_path = os.path.join(check_path, filename)
    check_image.save(check_image_path, format='PNG')
    with open(check_image_path, 'rb') as f:
        instance.check_qr_text.save(filename, File(f), save=False)
    instance.save()

