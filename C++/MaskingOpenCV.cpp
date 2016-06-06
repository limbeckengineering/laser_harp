//============================================================================
// Name        : MaskingOpenCV.cpp
// Author      : j
// Version     :
// Copyright   : Your copyright notice
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <iostream>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;


int main() {

	VideoCapture cap(0);

	Mat frame;

	int width, height;

	width = cap.get(CV_CAP_PROP_FRAME_WIDTH);
	height = cap.get(CV_CAP_PROP_FRAME_HEIGHT);

	cout << width << endl;
	cout << height << endl;

	Mat mask(width, height, CV_8UC1, Scalar::all(0));

	Rect ROI(100, 100, 300, 300
			);

	mask(ROI).setTo(Scalar::all(255));

	namedWindow("Mask", WINDOW_AUTOSIZE);

	while((char)waitKey(10) != 'c'){

		cap >> frame;

		imshow("Mask", frame(ROI));

		Scalar mean_value = mean(frame(ROI));

		cout << mean_value[1] << endl;

	}

	return 0;
}
