import cv2
import pytesseract
from PIL import Image

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = 'C:/Users/Irfan/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

# Open a connection to the camera (usually 0 for built-in webcam)
cap = cv2.VideoCapture(0)

while True:
    _, image = cap.read()
    cv2.imshow("Text Detection", image)
    key = cv2.waitKey(1)

    if key == ord('s'):
        cv2.imwrite("C:/Users/Irfan/PycharmProjects/Medicine_Finder/test1.jpg", image)
        break

cap.release()
cv2.destroyAllWindows()

def tesseract():
    Imagepath = 'C:/Users/Irfan/PycharmProjects/Medicine_Finder/test1.jpg'
    text = pytesseract.image_to_string(Image.open(Imagepath))
    print(text[:-1])

tesseract()
