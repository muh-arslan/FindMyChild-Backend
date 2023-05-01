import face_recognition
# import cv2
# from keras_facenet import FaceNet
# from django.conf import settings


# def face_detection(image):
#     model_path = settings.STATIC_URL + 'Models/haarcascade_profileface.xml'
#     profile_cascade = cv2.CascadeClassifier(model_path)
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     profiles = profile_cascade.detectMultiScale(
#         gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
#     if (len(profiles) == 0):
#         gray = cv2.flip(gray, 1)
#         profiles = profile_cascade.detectMultiScale(
#             gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
#     if (len(profiles) == 0):
#         return -1

#     for j, (x, y, w, h) in enumerate(profiles):
#         face_img = image[y:y+h, x:x+w]
#     return face_img


# def preprocess_image(image):
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     image = cv2.resize(image, (160, 160))
#     return image


def feature_extractor(image_path):
    image = face_recognition.load_image_file(image_path)
    try:
        image_encoding = face_recognition.face_encodings(image)[0]
    except:
        # try:
        #     image = face_detection(image)
        #     preprocessed_image = preprocess_image(image)
        #     embedder = FaceNet()
        #     image_encoding = embedder.embeddings([preprocessed_image])
        # except:
        image_encoding = None
    return image_encoding


def match_results(image1_encoding, image2_encoding):
    try:
        result = face_recognition.compare_faces(
            [image1_encoding], image2_encoding)
        distance = face_recognition.face_distance(
            [image1_encoding], image2_encoding)
        # print("distance: ", distance[0])
    except:
        return False, None
    return result[0], distance[0]
