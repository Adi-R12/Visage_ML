import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import qrcode
import io
from reportlab.lib.utils import ImageReader

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://paperless-boarding-system-default-rtdb.firebaseio.com/",
    'storageBucket': "paperless-boarding-system.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/background.png')

# # Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

# Load the encoding file
# print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []
check=False
studentInfo = {}

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            print("matches", matches)
            print("faceDis", faceDis)


            matchIndex = np.argmin(faceDis)
            # print("Match Index", matchIndex)

            if matches[matchIndex]:
                if faceDis[matchIndex]<0.5:
                    print("Known Face Detected")
                    if check:
                        cap.release()
                        # Generate the QR code in memory
                        qr = qrcode.QRCode(
                            version=1,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=10,
                            border=4,
                        )
                        qr.add_data(str(studentInfo))
                        qr.make(fit=True)

                        # Create an in-memory image for the QR code
                        img = qr.make_image(fill_color="black", back_color="white")

                        # Create a PDF file
                        pdf_filename = 'boarding_pass.pdf'
                        c = canvas.Canvas(pdf_filename, pagesize=letter)

                        # Set the title
                        c.setFont("Helvetica", 16)
                        c.drawString(200, 750, "Boarding Pass")

                        # Passenger information
                        c.setFont("Helvetica", 12)
                        x, y = 50, 700
                        for key, value in studentInfo.items():
                            c.drawString(x, y, f"{key}: {value}")
                            y -= 20

                        # Draw the QR code on the PDF
                        imgByteArr = io.BytesIO()
                        img.save(imgByteArr, format='PNG')
                        imgByteArr = imgByteArr.getvalue()

                        # Create an ImageReader from the binary image data
                        img_reader = ImageReader(io.BytesIO(imgByteArr))

                        # Embed the image in the PDF using the ImageReader
                        c.drawImage(img_reader, 400, 550, width=100, height=100)

                        # Save the PDF
                        c.save()
                        print(f'Boarding pass saved as {pdf_filename}')
                        break

                    print(studentIds[matchIndex])
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                    id = studentIds[matchIndex]
                    if counter == 0:
                        studentInfo = db.reference(f'Users/{id}').get()
                        cvzone.putTextRect(imgBackground, studentInfo["name"], (275, 400))
                        cv2.imshow("Face Attendance", imgBackground)
                        cv2.waitKey(1)
                        counter = 1
                        modeType = 1
                # else:
                #      cv2.putText(imgBackground, str('No User Found'), (1006, 550),
                #                 cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        if counter != 0:
            if counter == 1:
                # Get the Data
                studentInfo = db.reference(f'Users/{id}').get()
                print(studentInfo)
                # Get the Image from the storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                # Update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)

                if secondsElapsed > 30:
                    ref = db.reference(f'Users/{id}')
                    # studentInfo['total_attendance'] += 1
                    # ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                    # cap1 = cv2.VideoCapture(0)
                    # cap1.set(3, 640)
                    # cap1.set(4, 480)
            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                    check = True

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 100:
                    cv2.putText(imgBackground, str(studentInfo['Flight_No']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['Seat_No']), (840, 650),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['Departure']), (930, 650),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['PNR']), (1100, 650),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w)
                    cv2.putText(imgBackground, str(studentInfo['name']), (650 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgStudent = cv2.resize(imgStudent, (216, 216))

                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent
                counter += 1
                if counter >= 100:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
