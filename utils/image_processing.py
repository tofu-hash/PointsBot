from PIL import (Image, ImageDraw,
                 ImageFont)


def make_points_count_img(points_count: int):
    """Рисует картинку с количеством поинтов."""

    img = Image.open('./source/service/point.jpg')
    draw = ImageDraw.Draw(img)

    helvetica_bold_big_font = ImageFont.truetype('source/fonts/helvetica_bold.otf',
                                                 size=80)
    helvetica_bold_small_font = ImageFont.truetype('source/fonts/helvetica_bold.otf',
                                                 size=45)
    size_x, size_y = img.size
    # Draw quote text
    draw.text(
        (int(size_x / 2), int(size_y / 2) - 40), str(points_count),
        anchor="mm",
        font=helvetica_bold_big_font,
        fill='white'
    )
    draw.text(
        (int(size_x / 2), int(size_y / 2) + 30), 'поинтов',
        anchor="mm",
        font=helvetica_bold_small_font,
        fill='white'
    )

    img.save('./source/service/result.jpg')


make_points_count_img(9)