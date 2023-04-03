import cv2
import face_recognition
from keras_facenet import FaceNet


def face_detection(image):
    profile_cascade = cv2.CascadeClassifier(
        'Models/haarcascade_profileface.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    profiles = profile_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if (len(profiles) == 0):
        gray = cv2.flip(gray, 1)
        profiles = profile_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    if (len(profiles) == 0):
        return -1

    for j, (x, y, w, h) in enumerate(profiles):
        face_img = image[y:y+h, x:x+w]
    return face_img


def preprocess_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (160, 160))
    return image


def feature_extraction(image):
    try:
        image_encoding = face_recognition.face_encodings(image)[0]
    except:
        try:
            image = face_detection(image)
            preprocessed_image = preprocess_image(image)
            embedder = FaceNet()
            image_encoding = embedder.embeddings([preprocessed_image])
        except:
            image_encoding = []
    return image_encoding


def match_results(image1_encoding, image2_encoding):
    try:
        result = face_recognition.compare_faces(
            [image1_encoding], image2_encoding)
    except:
        try:
            image2_encoding = image2_encoding.reshape(1, -1)
            result = face_recognition.compare_faces(
                [image1_encoding], image2_encoding)
        except:
            return False
    return result[0]