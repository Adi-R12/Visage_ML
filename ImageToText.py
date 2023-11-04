import cv2
import pytesseract
import re
import numpy as np

# Function to capture an image from the webcam
def capture_image():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Couldn't open the webcam")
        return None

    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()

        if not ret:
            print("Error: Couldn't capture a frame")
            break

        # Display the frame from the webcam
        cv2.imshow("Webcam", frame)

        # Check for the 'q' key press
        key = cv2.waitKey(1)
        if key == ord('q'):
            # Capture the current frame in memory (NumPy array)
            captured_frame = frame.copy()
            print("Image captured temporarily")
            break

    cap.release()

    cv2.destroyAllWindows()

    if captured_frame is not None:
        extracted_text = extract_text(captured_frame)
        if extracted_text:
            # Extract Aadhar number
            aadhar_number = extract_aadhar_number(extracted_text)
            if aadhar_number:
                print("Extracted Aadhar Number:", aadhar_number)
            else:
                print("Aadhar number not found in the text")

def extract_text(frame):
    try:
        text = pytesseract.image_to_string(frame)
        return text
    except Exception as e:
        print(f"Error during text extraction: {str(e)}")
        return None

def extract_aadhar_number(text):
    aadhar_pattern = r'\d{4}[\s-]?\d{4}[\s-]?\d{4}'
    aadhar_match = re.search(aadhar_pattern, text)
    if aadhar_match:
        return aadhar_match.group().replace(" ", "").replace("-", "")
    return None

if __name__ == "__main__":
    capture_image()

