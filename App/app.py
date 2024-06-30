from flask import Flask, render_template, Response
import cv2 as cv
import mediapipe as mp

app = Flask(__name__)

cap = cv.VideoCapture(0)
mphand = mp.solutions.hands
hands = mphand.Hands(min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils
fingercordinates = [(8, 6), (12, 10), (16, 14), (20, 18)]
thumbcordinates = [4, 2]

def generate_frames():
    while True:
        success, img = cap.read()
        if not success:
            break
        else:
            imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            result = hands.process(imgRGB)
            multi = result.multi_hand_landmarks
            if multi:
                handPoins = []
                for handsLMS in multi:
                    mpDraw.draw_landmarks(img, handsLMS, mphand.HAND_CONNECTIONS)
                    for idx, ln in enumerate(handsLMS.landmark):
                        h, w, c = img.shape
                        cx, cy = int(w * ln.x), int(h * ln.y)
                        handPoins.append((cx, cy))
                    for points in handPoins:
                        cv.circle(img, points, 10, (255, 0, 0), cv.FILLED)
                    count = 0
                    for coordinate in fingercordinates:
                        if handPoins[coordinate[0]][1] < handPoins[coordinate[1]][1]:
                            count += 1
                    if handPoins[thumbcordinates[0]][0] > handPoins[thumbcordinates[1]][0]:
                        count += 1
                    if count == 5:
                        cv.putText(img, "hai", (100, 150), cv.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 5)
                    elif handPoins[fingercordinates[0][0]] > handPoins[fingercordinates[0][1]] and handPoins[fingercordinates[1][0]] > handPoins[fingercordinates[1][1]]:
                        cv.putText(img, "peace", (100, 150), cv.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 5)
                    elif count == 0:
                        cv.putText(img, "hello", (100, 150), cv.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 5)
                    elif count == 3:
                        cv.putText(img, "super", (100, 150), cv.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 5)
                    elif count == 1 and handPoins[thumbcordinates[0]] > handPoins[thumbcordinates[1]]:
                        cv.putText(img, "like", (100, 150), cv.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 5)
            ret, buffer = cv.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('login.html')
@app.route('/login')
def home():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
