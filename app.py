import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import os
import io
from zipfile import ZipFile


# Function to auto-enhance and upscale a single image
def auto_enhance_and_upscale_image(img, scale_factor=2, color_factor=1.5, brightness_factor=1.2, contrast_factor=1.3):
    # Step 1: Enhance the color
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(color_factor)  # Default color enhancement

    # Step 2: Enhance brightness and contrast
    brightness_enhancer = ImageEnhance.Brightness(img)
    img = brightness_enhancer.enhance(brightness_factor)  # Default brightness enhancement

    contrast_enhancer = ImageEnhance.Contrast(img)
    img = contrast_enhancer.enhance(contrast_factor)  # Default contrast enhancement

    # Step 3: Sharpen the image to reduce blur
    img = img.filter(ImageFilter.SHARPEN)

    # Get the current size of the image
    width, height = img.size

    # Step 4: Upscale the image using a high-quality resampling filter
    new_size = (int(width * scale_factor), int(height * scale_factor))
    upscaled_img = img.resize(new_size, Image.LANCZOS)

    return upscaled_img

# Function to process multiple images and return them as a zip file
def process_images(files, scale_factor, color_factor, brightness_factor, contrast_factor):
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "a") as zf:
        for uploaded_file in files:
            img = Image.open(uploaded_file)
            enhanced_img = auto_enhance_and_upscale_image(
                img, scale_factor, color_factor, brightness_factor, contrast_factor
            )
            
            img_byte_arr = io.BytesIO()
            enhanced_img.save(img_byte_arr, format="PNG")
            zf.writestr(uploaded_file.name, img_byte_arr.getvalue())
    
    return zip_buffer.getvalue()

# Streamlit app
st.title('Image Enhancement and Upscaling')

# Sidebar with image enhancement options (optional for manual adjustment)
st.sidebar.title("Enhancement Options (Optional)")
auto_enhance = st.sidebar.checkbox("Auto-Enhance (Recommended)", value=True)
if not auto_enhance:
    color_factor = st.sidebar.slider("Color Enhancement", min_value=0.0, max_value=3.0, value=1.5, step=0.1)
    brightness_factor = st.sidebar.slider("Brightness", min_value=0.0, max_value=3.0, value=1.2, step=0.1)
    contrast_factor = st.sidebar.slider("Contrast", min_value=0.0, max_value=3.0, value=1.3, step=0.1)
else:
    color_factor, brightness_factor, contrast_factor = 1.5, 1.2, 1.3  # Auto-enhance default values

# Main interface for uploading images
st.write("Upload images or select a folder to enhance and upscale:")
uploaded_files = st.file_uploader("Choose images", type=["png", "jpg", "jpeg", "bmp", "gif", "webp"], accept_multiple_files=True)

# Number input for scale factor
scale_factor = st.number_input("Scale Factor", min_value=1, max_value=10, value=2)

if uploaded_files:
    if len(uploaded_files) == 1:
        # Process a single image
        img = Image.open(uploaded_files[0])
        enhanced_img = auto_enhance_and_upscale_image(img, scale_factor, color_factor, brightness_factor, contrast_factor)
        
        # Display the original and enhanced images side by side
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption='Original Image', use_column_width=True)
        with col2:
            st.image(enhanced_img, caption='Enhanced Image (Auto)', use_column_width=True)

        # Save and provide download link for enhanced image
        buffered = io.BytesIO()
        enhanced_img.save(buffered, format="PNG")
        st.download_button(
            label="Download Enhanced Image",
            data=buffered.getvalue(),
            file_name="enhanced_image.png",
            mime="image/png"
        )
    else:
        # Process multiple images
        st.write(f"Processing {len(uploaded_files)} images...")
        zip_data = process_images(uploaded_files, scale_factor, color_factor, brightness_factor, contrast_factor)

        # Provide download link for the zip file
        st.download_button(
            label="Download All Enhanced Images as ZIP",
            data=zip_data,
            file_name="enhanced_images.zip",
            mime="application/zip"
        )