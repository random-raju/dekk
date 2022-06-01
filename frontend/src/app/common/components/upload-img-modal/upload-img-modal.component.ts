import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-upload-img-modal',
  templateUrl: './upload-img-modal.component.html',
  styleUrls: ['./upload-img-modal.component.scss']
})
export class UploadImgModalComponent implements OnInit {

  constructor(public dialogRef: MatDialogRef<UploadImgModalComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any) { }

  file: File;
  fileUploaded = false;
  uploadComplete = false;

  ngOnInit(): void {
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  onUpload(): void {
    const imageFormData = new FormData();
    imageFormData.append('image', this.file, this.file.name); // TODO to upload

    // After upload: setting up final behavior
    this.uploadComplete = true;
    this.data.callback(this.data.cardId);
  }

  onFileSelected($event: any): void {
    if ($event?.target?.files?.length > 0) {
      this.file = $event.target.files[0];
      this.fileUploaded = true;
    }
  }

  getFileName(): string {
    if (this.file?.name) {
      return this.file.name;
    }
    return '';
  }

  removeFile(): void {
    this.fileUploaded = false;
  }
}
