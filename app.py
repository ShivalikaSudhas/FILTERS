"""
app.py - EdgeCam Hugging Face Web Application
----------------------------------------------
Provides a clean web-based webcam interface using Gradio for hosting on Hugging Face Spaces.
Allows users to run real-time Canny Edge Detection directly in any web browser without installation.
"""

import gradio as gr
import cv2
import numpy as np


def process_webcam_frame(image, blur_kernel: int, threshold1: int, threshold2: int):
    """
    Applies real-time Edge Detection with strict input bounds.
    """
    if image is None:
        return None

    # Input validation & Rate/Bound limiting
    blur_kernel = int(max(1, min(31, blur_kernel)))
    if blur_kernel % 2 == 0:
        blur_kernel += 1

    threshold1 = int(max(0, min(255, threshold1)))
    threshold2 = int(max(0, min(255, threshold2)))

    # Process RGB image from browser
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)
    edges = cv2.Canny(blur, threshold1, threshold2)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)


# Create Gradio Web Interface
with gr.Blocks(title="⚡ EdgeCam - Realtime Edge Detection Studio") as demo:
    gr.Markdown("# ⚡ EdgeCam - Realtime Edge Detection Studio")
    gr.Markdown("Real-time webcam Canny Edge Detection studio hosted on Hugging Face Spaces.")

    with gr.Row():
        with gr.Column():
            webcam_input = gr.Image(sources=["webcam"], streaming=True, label="Live Camera")
            
            blur_slider = gr.Slider(minimum=1, maximum=31, step=2, value=5, label="Blur Kernel")
            t1_slider = gr.Slider(minimum=0, maximum=255, step=1, value=50, label="Canny Threshold 1")
            t2_slider = gr.Slider(minimum=0, maximum=255, step=1, value=120, label="Canny Threshold 2")
            
            reset_btn = gr.Button("🔄 Reset Sliders to Defaults")

        with gr.Column():
            output_image = gr.Image(label="Processed Edge Output")

    # Frame processing connection
    inputs = [webcam_input, blur_slider, t1_slider, t2_slider]
    webcam_input.stream(fn=process_webcam_frame, inputs=inputs, outputs=output_image)

    # Reset button handler
    def reset_defaults():
        return 5, 50, 120

    reset_btn.click(fn=reset_defaults, inputs=[], outputs=[blur_slider, t1_slider, t2_slider])

if __name__ == "__main__":
    demo.launch()
