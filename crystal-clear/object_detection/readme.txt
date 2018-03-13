To run:
		python classify_image.py

Optional parameters:

		--image_file
	Directory and filename of image to classify, defaults to ./tests/pencil.jpg

		--model_dir
	Directory of model data, defaults to ./tmp/imagenet

		--num_top_predictions
	Number of guesses to return, defaults to 5

Example:

		python classify_image --image_file ./tests/cropped_panda.jpg
	Returns top 5 guesses of cropped_panda.jpg, using the InceptionV3 model