import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)


    def __init__(self, video_path, audio_path, output_path, video_folder=None, audio_folder=None):
        super().__init__()
        self.video_path = video_path
        self.audio_path = audio_path
        self.output_path = output_path
        self.video_folder = video_folder
        self.audio_folder = audio_folder

    def combine_audio_and_video(self):
        """Combine audio and video streams using FFmpeg."""
        try:
            subprocess.call(['ffmpeg', '-i', self.video_path, '-i', self.audio_path, '-c:v', 'copy', '-c:a', 'copy', '-map', '0:v:0', '-map', '1:a:0', self.output_path])
            self.finished.emit()
        except Exception as e:
            print(f"Error combining audio and video: {e}")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.video_filename = None
        self.audio_filename = None
        self.output_folder = None
        self.audio_folder = None
        self.video_folder = None
        self.extract_audio_button = None
        self.progress_bar = None
        self.combine_folder_checkbox = None

        # Create the GUI
        self.setWindowTitle('Combine Audio and Video')
        self.setMinimumSize(400, 200)

         # Initialize labels
        self.video_label = QLabel('No video file selected.')
        self.audio_label = QLabel('No audio file selected.')


              # Add a QLabel to display the number of audio files found
        self.audio_count_label = QLabel("Number of audio files found: 0", self)
        self.video_count_label = QLabel("Number of video files found: 0", self)
       
        self.checkbox = QCheckBox('select folder')

        # Create the labels and buttons for selecting video and audio files
        self.video_label = QLabel('No video file selected.')
        self.video_button = QPushButton('Select Video')
        self.video_button.clicked.connect(self.select_video_folder)

        self.audio_label = QLabel('No audio file selected.')
        self.audio_button = QPushButton('Select Audio')
        self.audio_button.clicked.connect(self.select_audio_folder)

        # Changed from QCheckBox to QPushButton
        self.extract_audio_button = QPushButton('Extract Extra Audio from Video')
        self.extract_audio_button.setEnabled(False)
        self.extract_audio_button.clicked.connect(self.extract_audio_from_video)

        # Create the button for selecting the output folder
        self.output_label = QLabel('No output folder selected.')
        self.output_button = QPushButton('Select Output Folder')
        self.output_button.clicked.connect(self.select_output_folder)

        # Create the button for combining audio and video files
        self.combine_button = QPushButton('Combine Audio and Video')
        self.combine_button.setEnabled(False)
        self.combine_button.clicked.connect(self.combine_audio_and_video)

            # Changed from QCheckBox to QPushButton
        # self.convert_video_format = QPushButton('Change video format')
        # self.convert_video_format.setEnabled(False)
        # self.convert_video_format.clicked.connect(self.change_video_format)



        #  # Create a dropdown for output format selection
        # self.output_format_label = QLabel('Select Output Format:')
        # self.output_format_combo = QComboBox(self)
        # self.output_format_combo.addItem("MP4")
        # self.output_format_combo.addItem("WebM")
        # self.output_format_combo.addItem("AVI")


        # # Add to layout
        # format_layout = QHBoxLayout()
        # format_layout.addWidget(self.output_format_label)
        # format_layout.addWidget(self.output_format_combo)
        # # format_layout.addWidget(self.convert_video_format)

       


        # Define the layouts
        video_layout = QHBoxLayout()
        video_layout.addWidget(self.video_label)
        video_layout.addWidget(self.video_button)

        audio_layout = QHBoxLayout()
        audio_layout.addWidget(self.audio_label)
        audio_layout.addWidget(self.audio_button)

        extract_audio_layout = QHBoxLayout()
        extract_audio_layout.addWidget(self.extract_audio_button)
        extract_audio_layout.addWidget(self.checkbox)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.combine_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(video_layout)
        main_layout.addLayout(audio_layout)
        main_layout.addLayout(extract_audio_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.audio_count_label)
        main_layout.addWidget(self.video_count_label)
        # main_layout.addLayout(format_layout)

        # Create the progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setVisible(False)

        # Apply styles
        stylesheet = """
            QLabel {
                font-size: 16px;
            }
            QPushButton {
                font-size: 16px;
                padding: 8px;
                border-radius: 8px;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #3e8e41;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        self.setStyleSheet(stylesheet)

        self.setLayout(main_layout)





    def file_exists(self, file_path):
        """Check if a file exists."""
        return os.path.exists(file_path)

    def get_new_filename(self, existing_path):
        """Generate a new filename by appending a number."""
        base, ext = os.path.splitext(existing_path)
        counter = 1
        while True:
            new_path = f"{base}_{counter}{ext}"
            if not self.file_exists(new_path):
                return new_path
            counter += 1

    def confirm_overwrite(self, output_path):
        """Prompt the user to confirm overwrite, rename, or skip."""
        choice = QMessageBox.question(
            self, 'File Overwrite Confirmation',
            f'The file {output_path} already exists. Do you want to overwrite it?',
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        if choice == QMessageBox.Yes:
            return True
        elif choice == QMessageBox.No:
            new_path = self.get_new_filename(output_path)
            return new_path
        else:
            return False


    def select_audio_folder(self):
        options = QFileDialog.Options()
    
        # Ask the user if they want to select a file or a folder
       
    
        if self.checkbox.isChecked():
            # Select a folder containing audio files
            self.audio_folder = QFileDialog.getExistingDirectory(self, "Select Audio Folder", options=options)
            if self.audio_folder:
                self.audio_label.setText(self.audio_folder)
                self.enable_combine_button()

            audio_extensions = ('.mp3', '.wav', '.ogg', '.aac','.mp4', '.m4a')
            audio_files = [f for f in os.listdir(self.audio_folder) if f.endswith(audio_extensions)]
            total_files = len(audio_files)
            self.audio_count_label.setText(f"Number of audio files found: {total_files} ")  # Update label

        else:
            # Select a single audio file
            self.audio_filename, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.ogg);;All Files (*)", options=options)
            if self.audio_filename:
                self.audio_label.setText(os.path.basename(self.audio_filename))
                self.enable_combine_button()
    
    def select_video_folder(self):
        options = QFileDialog.Options()
    
        # Ask the user if they want to select a file or a folder
   
        if self.checkbox.isChecked():
            # Select a folder containing video files
            self.video_folder = QFileDialog.getExistingDirectory(self, "Select Video Folder", options=options)
            if self.video_folder:
                self.video_label.setText(self.video_folder)
                self.enable_combine_button()
                
            
            video_extensions = ('.mp4', '.avi', '.mkv', '.flv', '.mov', '.wmv')
            video_files = [f for f in os.listdir(self.video_folder) if f.endswith(video_extensions)]
            total_videofiles = len(video_files)
            self.video_count_label.setText(f"Number of video files found: {total_videofiles} ")  # Update label
        else:
               # Select a single video file
            self.video_filename , _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.avi *.mkv *.mov);;All Files (*)", options=options)
            if self.video_filename:
                self.video_label.setText(os.path.basename(self.video_filename))
                self.enable_combine_button()
             



    def select_output_folder(self):
        # Open a file dialog to select the output folder
        self.output_folder = QFileDialog.getExistingDirectory(self, 'Select Output Folder')

        # Update the output label with the selected folder path
        if self.output_folder:
            self.output_label.setText(self.output_folder)
            self.enable_combine_button()






    # def change_video_format(self):

       
    #     # Check the selected output format
       
    #     output_format = self.output_format_combo.currentText()
        
    #     codec = 'copy'  # Default to copy for most formats, change as needed
        
    #     # Map the output format to the appropriate FFmpeg codec or command
    #     if output_format == "MP4":
    #         output_extension = ".mp4"
    #     elif output_format == "WebM":    
    #         output_extension = ".webm"
    #     elif output_format == "AVI":
    #         output_extension = ".avi"
    #     # Add more format mappings as needed
    #     # if  self.checkbox.isChecked():
        
    #     video_extensions = ('.mp4', '.avi', '.mkv', '.flv', '.mov', '.wmv')
        
    #     video_files = [f for f in os.listdir(self.video_folder) if f.endswith(video_extensions)]
        
    #     for video_file in video_files:
    #             video_path = os.path.join(self.video_folder, video_file)
    #             output_path = os.path.join(self.output_folder, video_file.replace(os.path.splitext(video_file)[1], output_extension))
    #     try:
    #             subprocess.call(['ffmpeg', '-i', video_path, '-c', codec , output_path])
    #             QMessageBox.information(self,'information',f"Successfully converted {video_file} to {output_format} format.")
    #     except Exception as e:
    #             QMessageBox.warning(self,'warning',f"Error converting video {video_file}: {e}")
    #     # else:
    #     #     video_path = self.video_filename   
    #     #     try:

    #     #         output_path = os.path.join(self.output_folder, video_path)
    #     #         subprocess.call(['ffmpeg', '-i', video_path, '-c', codec , output_path])
    #     #         QMessageBox.information(self,'information',f"Successfully converted {video_path} to {output_format} format.")
    #     #     except Exception as e:
    #     #         QMessageBox.warning(self,'warning',f"Error converting video {video_path}: {e}")


    def extract_audio_from_video(self):
        if self.video_filename:
            output_filename = os.path.join(os.path.dirname(self.video_filename), 'extra_audio.mp3')
            subprocess.call(['ffmpeg', '-i', self.video_filename, '-vn', '-acodec', 'copy', output_filename])
            self.audio_filename = output_filename
            self.audio_label.setText(os.path.basename(self.audio_filename))
            self.enable_combine_button()

            # Display a success message box
            QMessageBox.information(self, 'Success', 'Extra audio extracted successfully.')

    def enable_combine_button(self):
    # Check if single file paths and output folder are selected
        if self.video_filename and self.audio_filename and self.output_folder:
            self.combine_button.setEnabled(True)
        # Check if folder paths and output folder are selected
        elif self.video_folder and self.audio_folder and self.output_folder:
            self.combine_button.setEnabled(True)

        elif self.video_folder and self.output_folder:
            # self.convert_video_format.setEnabled(True)
            self.extract_audio_button.setEnabled(True)
        elif self.video_filename and self.output_folder:
            # self.convert_video_format.setEnabled(True)
            self.extract_audio_button.setEnabled(True)
        else:
            self.combine_button.setEnabled(False)


    def combine_audio_and_video(self):
        try :
            if self.video_filename and self.audio_filename and self.output_folder:
               self.combine_audio_and_video_single_file()
     
            else:
                try:

                    if not self.video_folder:
                       QMessageBox.warning(self, "Warning", "Please select  audio folder.")
                       return
                    if not self.video_folder:
                        QMessageBox.warning(self, "Warning", "Please select  video folder.")
                        return
                    if not self.output_folder:
                         QMessageBox.warning(self, "Warning", "Please select  output folder.")
                         return
           # Handle the case where the necessary paths or files are not set.
            # Display an error message or take appropriate action.
                    self.combine_audio_and_video_folder()
                      
                except Exception as e:
                        QMessageBox.warning(self, 'not connect to combine folder method', str(e))


        except Exception as e:
                QMessageBox.warning(self, 'not connect to combine method', str(e))

    def combine_audio_and_video_folder(self):
        
        try:

               # Extend the list of acceptable video and audio file types
            video_extensions = ('.mp4', '.avi', '.mkv', '.flv', '.mov', '.wmv')
            audio_extensions = ('.mp3', '.wav', '.ogg', '.aac','.mp4', '.m4a')


            audio_files = [f for f in os.listdir(self.audio_folder) if f.endswith(audio_extensions)]
            video_files = [f for f in os.listdir(self.video_folder) if f.endswith(video_extensions)]
          

            success_count = 0  # To keep track of successfully merged files
            for video_file in video_files:
                video_path = os.path.join(self.video_folder, video_file)
                
                # Generate potential audio filenames based on current video file
                potential_audio_files = [video_file.replace(ext, audio_ext) for ext in video_extensions for audio_ext in audio_extensions]
                
                # Find the first matching audio file
                audio_path = next((os.path.join(self.audio_folder, audio_file) for audio_file in potential_audio_files if audio_file in audio_files), None)
                
                if audio_path:
                    output_path = os.path.join(self.output_folder, video_file)
              
                    if self.file_exists(output_path):
                        result = self.confirm_overwrite(output_path)
                        if not result:
                            continue
                        elif result is not True:
                             output_path = result

                    subprocess.call(['ffmpeg', '-i', video_path, '-i', audio_path, '-c:v', 'copy', '-c:a', 'copy', '-map', '0:v:0', '-map', '1:a:0', '-map_metadata', '0', output_path])
                    success_count += 1
                else:
                    QMessageBox.warning(self,'warning',f"No matching video file found")  # Debugging print
                    return
              # Display success message after the loop completes
            if success_count == len(video_files):
                QMessageBox.information(self, 'Success', 'Successfully merged all audio and video files.')
            else:
                QMessageBox.warning(self, 'Incomplete', 'Some files could not be merged.')

        except Exception as e:
                QMessageBox.warning(self, 'no audio video found  ', str(e))


    def combine_audio_and_video_single_file(self):
        video_path = self.video_filename
        audio_path = self.audio_filename
        output_filename = os.path.splitext(os.path.basename(video_path))[0] + '_combined.mp4'
        output_path = os.path.join(self.output_folder, output_filename)
     
     
        if self.file_exists(output_path):
            result = self.confirm_overwrite(output_path)
            if not result:
                return
            elif result is not True:
                output_path = result

        worker = Worker(video_path, audio_path, output_path)
        worker.finished.connect(self.combine_finished)
        worker.progress.connect(self.update_progress)

        with ThreadPoolExecutor() as executor:
            executor.submit(worker.combine_audio_and_video)

        self.progress_bar.setVisible(True)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def combine_finished(self):
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, 'Success', 'Audio and video combined successfully.')
        self.reset_gui()

    def reset_gui(self):
        self.video_filename = None
        self.audio_filename = None
        self.output_folder = None
        self.video_folder = None  # Define video_folder
        self.audio_folder = None  # Define audio_folder
        self.video_label.setText('No video file selected.')
        self.audio_label.setText('No audio file selected.')
        self.output_label.setText('No output folder selected.')
        self.combine_button.setEnabled(False)
        self.extract_audio_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
