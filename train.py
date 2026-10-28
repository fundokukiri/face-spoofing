import tensorflow as tf
import numpy as np
from facenet.src import facenet
import os
import math
import pickle
from sklearn.svm import SVC 
import shutil

if os.path.exists("FacePay/Models/temp/FaceNet_Model.pkl"):
    os.remove("FacePay/Models/temp/FaceNet_Model.pkl")

data_train_dir = "FacePay/static/Data/FaceNet"
model_dir = "FacePay/Models/FaceNet_Model.pb"
model_pickle_dir = "FacePay/Models/temp/FaceNet_Model.pkl"
BATH_SIZE = 8
IMAGES_SIZE = 160

def main():  
    with tf.Graph().as_default():     
        with tf.compat.v1.Session() as sess:            
            dataset = facenet.get_dataset(data_train_dir)             
            paths, labels = facenet.get_image_paths_and_labels(dataset)            
            print('Number of classes: %d' % len(dataset))
            print('Number of images: %d' % len(paths))           
            # Load the model
            print('Loading feature extraction model')
            facenet.load_model(model_dir)            
            # Get input and output tensors
            images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("phase_train:0")
            embedding_size = embeddings.get_shape()[1]
            # Run forward pass to calculate embeddings
            print('Calculating features for images')
            nrof_images = len(paths)
            nrof_batches_per_epoch = int(math.ceil(1.0*nrof_images / BATH_SIZE))
            emb_array = np.zeros((nrof_images, embedding_size))
            for i in range(nrof_batches_per_epoch):
                start_index = i*BATH_SIZE
                end_index = min((i+1)*BATH_SIZE, nrof_images)
                paths_batch = paths[start_index:end_index]
                images = facenet.load_data(paths_batch, False, False, IMAGES_SIZE)
                feed_dict = { images_placeholder:images, phase_train_placeholder:False }
                emb_array[start_index:end_index,:] = sess.run(embeddings, feed_dict=feed_dict)           
            classifier_filename_exp = os.path.expanduser(model_pickle_dir)
            print('Training classifier')
            print(type(emb_array))
            model = SVC(kernel='linear', probability=True)
            model.fit(emb_array, labels)
        
            # Create a list of class names
            class_names = [ cls.name.replace('_', ' ') for cls in dataset]

            # Saving classifier model
            with open(classifier_filename_exp, 'wb') as outfile:
                pickle.dump((model, class_names), outfile)
            print('Saved classifier model to file "%s"' % classifier_filename_exp)                          

if __name__ == '__main__':
    main()
    if os.path.exists("FacePay/Models/FaceNet_Model.pkl"):
        os.remove("FacePay/Models/FaceNet_Model.pkl")
    if os.path.exists("FacePay/Models/temp/FaceNet_Model.pkl"):
        shutil.copyfile("FacePay/Models/temp/FaceNet_Model.pkl","FacePay/Models/FaceNet_Model.pkl") 

