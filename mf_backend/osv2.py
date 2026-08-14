from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from io import BytesIO




def getFontDimension(draw, line1, line2, font):
    text_width1 = draw.textlength(line1, font=font)
    text_width2 = draw.textlength(line2, font=font)

    text_box1 = draw.textbbox((0, 0), line1, font=font)
    text_box2 = draw.textbbox((0, 0), line2, font=font)
    text_height1 = text_box1[3] - text_box1[1]
    text_height2 = text_box2[3] - text_box2[1]

    return text_width1, text_width2, text_height1, text_height2


# def add_text_below_image(image, username , employee_id):
#     # font_path = "Roboto-MediumItalic.ttf"
#     font_path = "Roboto-Medium.ttf"
#     primary_color = "#EC1C24"
#     secondary_color = "#194172"
#     # Open the original image
#     # image = Image.open(image_path)
#     image_width, image_height = image.size

#     # Define the texts to add
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     line1 = f"User: {username}-{employee_id}"
#     line2 = f"Timestamp: {timestamp}"

#     # Determine a base font size proportional to the image height
#     base_font_size = int(image_height * 0.02)  # 5% of image height
#     padding = int(image_height * 0.01)
#     # base_font_size = 3
#     print(f"base_font_size: {base_font_size}")

#     # Load a truetype or default font
#     try:
#         print("in try")
#         font = ImageFont.truetype(font_path, base_font_size)
#     except IOError as e:
#         print("Error: ")
#         print(str(e))
#         font = ImageFont.load_default()

#     # Adjust the font size dynamically
#     draw = ImageDraw.Draw(image)
#     # text_width1, text_height1 = draw.textsize(line1, font=font)
#     # text_width2, text_height2 = draw.textsize(line2, font=font)
#     # text_height = text_height1 + text_height2

#     # text_width1 = draw.textlength(line1, font=font)
#     # text_width2 = draw.textlength(line2, font=font)

#     # text_box1 = draw.textbbox((0, 0), line1, font=font)
#     # text_box2 = draw.textbbox((0, 0), line2, font=font)
#     # text_height1 = text_box1[3] - text_box1[1]
#     # text_height2 = text_box2[3] - text_box2[1]

#     # text_height = int(text_height1 + text_height2)
#     text_width1, text_width2, text_height1, text_height2 = getFontDimension(draw, line1, line2, font)
#     text_height = int(text_height1 + text_height2)
    
#     while text_width1 > image_width * 0.9 or text_width2 > image_width * 0.9:
#         base_font_size -= 1
#         if base_font_size < 10:
#             break
#         font = ImageFont.truetype(font_path, base_font_size)
#         text_width1, text_width2, text_height1, text_height2 = getFontDimension(draw, line1, line2, font)
#         text_height = int(text_height1 + text_height2)
        
#     print(f"text_width1: {text_width1}, text_width2: {text_width2}")
#     print(f"Total Height: {text_height}")

#     # Create a new image with extra space for the text
#     total_height = image_height + text_height + padding*3
#     new_image = Image.new("RGB", (image_width, total_height), "white")

#     # Paste the original image onto the new image
#     new_image.paste(image, (0, 0))

#     # # Draw the text onto the new image
#     # draw = ImageDraw.Draw(new_image)
#     # # text_x1 = (image_width - text_width1) // 2  # Center the first line of text horizontally
#     # # text_x2 = (image_width - text_width2) // 2  # Center the second line of text horizontally
#     # text_x1 = padding
#     # text_x2 = padding
#     # text_y1 = image_height + padding  # 20 pixels padding from the image
#     # text_y2 = text_y1 + text_height1 + padding  # Below the first line of text

#     # draw.text((text_x1, text_y1), line1, font=font, fill=primary_color)
#     # draw.text((text_x2, text_y2), line2, font=font, fill=primary_color)

#     # # Save the new image
#     # new_image.save(output_path)

#     # Draw the text onto the new image
#     draw = ImageDraw.Draw(new_image)
#     text_x1 = padding
#     text_x2 = padding
#     text_y1 = image_height + padding
#     text_y2 = text_y1 + text_height1 + padding

#     draw.text((text_x1, text_y1), line1, font=font, fill=primary_color)
#     draw.text((text_x2, text_y2), line2, font=font, fill=primary_color)

#     # Save the new image to a BytesIO object
#     output = BytesIO()
#     new_image.save(output, format='JPEG')
#     output.seek(0)
    
#     return output

# Example usage
# add_text_below_image("path/to/your/image.jpg", "path/to/output/image_with_text.jpg", "username123")

#add_text_below_image("aadhar_card.jpg", "aadhar_rotated_edited.jpg", "username123")


def add_text_below_image(image, username, employee_id):
    font_path = "Roboto-Medium.ttf"
    primary_color = "#EC1C24"
    
    image_width, image_height = image.size
    

    # Define the texts to add
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line1 = f"User: {username}-{employee_id}"
    line2 = f"Timestamp: {timestamp}"
   
    # Determine a base font size proportional to the image height
    base_font_size = int(image_height * 0.02)  # 2% of image height
    padding = int(image_height * 0.01)
    

    # Load a truetype or default font
    try:
        font = ImageFont.truetype(font_path, base_font_size)
        
    except IOError as e:
        font = ImageFont.load_default()

    # Calculate text dimensions
    draw = ImageDraw.Draw(image)
    text_box1 = draw.textbbox((0, 0), line1, font=font)
    text_box2 = draw.textbbox((0, 0), line2, font=font)
    text_width1, text_height1 = text_box1[2] - text_box1[0], text_box1[3] - text_box1[1]
    text_width2, text_height2 = text_box2[2] - text_box2[0], text_box2[3] - text_box2[1]
    text_height = int(text_height1 + text_height2)

    # Adjust the font size dynamically
    while text_width1 > image_width * 0.9 or text_width2 > image_width * 0.9:
        base_font_size -= 1
        if base_font_size < 10:
            
            break
        font = ImageFont.truetype(font_path, base_font_size)
        text_box1 = draw.textbbox((0, 0), line1, font=font)
        text_box2 = draw.textbbox((0, 0), line2, font=font)
        text_width1, text_height1 = text_box1[2] - text_box1[0], text_box1[3] - text_box1[1]
        text_width2, text_height2 = text_box2[2] - text_box2[0], text_box2[3] - text_box2[1]
        text_height = int(text_height1 + text_height2)

    # Create a new image with extra space for the text
    total_height = image_height + text_height + padding * 3
    new_image = Image.new("RGB", (image_width, total_height), "white")
    new_image.paste(image, (0, 0))

    # Draw the text onto the new image
    draw = ImageDraw.Draw(new_image)
    text_x = padding
    text_y1 = image_height + padding
    text_y2 = text_y1 + text_height1 + padding

    draw.text((text_x, text_y1), line1, font=font, fill=primary_color)
    draw.text((text_x, text_y2), line2, font=font, fill=primary_color)
    

    # Save the new image to a BytesIO object
    output = BytesIO()
    new_image.save(output, format='JPEG')
    output.seek(0)

    return output