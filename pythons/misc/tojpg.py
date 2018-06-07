import os, subprocess

def tojpg(inputDir, outputDir, ext = ".jpg"):
	if not os.path.isdir(outputDir):
		os.makedirs(outputDir)
	for root, dirs, files in os.walk(inputDir):
		for f in files:
			inputFile = os.path.join(root, f)
			fileName = os.path.splitext(f)[0]
			outputFile = os.path.join(outputDir, fileName + ext)

			command = "convert.exe %s %s"%(inputFile, outputFile)
			# print(command)
			subprocess.call(command, shell = True)

if __name__ == "__main__":
	tojpg("C:/Users/zwf/Documents/docs/ms/textures", "C:/Users/zwf/Documents/docs/ms/textures_jpg")
