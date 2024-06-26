import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import pickle


print(st.__version__)
print(cv2.__version__)
print(mp.__version__)


# Load model
@st.cache_resource
def load_model():
    model1_dict = pickle.load(open('./model.p', 'rb'))
    model1 = model1_dict['model']
    return model1


model = load_model()
st.title("Webcam Live Feed")
run = st.checkbox('Run')
FRAME_WINDOW = st.image([])

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3, max_num_hands=1)
labels_dict = {0: 'N', 1: 'O', 2: 'A', 3: 'H'}

camera = cv2.VideoCapture(0)


def process_frame(frame, model):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.flip(frame, 1)  # flip horizontal
    H, W, _ = frame.shape
    frame_rgb = frame.copy()
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        data_aux = []
        x_ = []
        y_ = []

        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                x_.append(x)
                y_.append(y)

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

        if x_ and y_:
            x1 = int(min(x_) * W) - 10
            y1 = int(min(y_) * H) - 10
            x2 = int(max(x_) * W) + 10
            y2 = int(max(y_) * H) + 10

            prediction = model.predict([np.asarray(data_aux)])
            predicted_character = labels_dict[int(prediction[0])]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 4)
            cv2.putText(frame,
                        predicted_character,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.3,
                        (255, 0, 0),
                        3,
                        cv2.LINE_AA)

    return frame


while run:
    _, frame = camera.read()
    frame = process_frame(frame, model)
    FRAME_WINDOW.image(frame)

else:
    st.write('Stopped Reading From Webcam')
