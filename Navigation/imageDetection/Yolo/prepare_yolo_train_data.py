import glob
import os

current_dir = os.getcwd()
percentage_test = 15 # Percentage of images to be used for the validation set

# Create train.txt and valid.txt
train_file = open('train.txt', 'w')  
test_file = open('valid.txt', 'w')

# Populate train.txt and valid.txt
counter = 1  
index_test = round(100 / percentage_test)

for file in glob.iglob(os.path.join(current_dir, '*.jpg')):  
    title, ext = os.path.splitext(os.path.basename(file))
    if counter == index_test:
        counter = 1
        test_file.write(current_dir + "/" + title + '.jpg' + "\n")
    else:
        train_file.write(current_dir + "/" + title + '.jpg' + "\n")
        counter = counter + 1