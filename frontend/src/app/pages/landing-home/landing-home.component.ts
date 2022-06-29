import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { SignupDialogComponent } from 'src/app/common/components/signup-dialog/signup-dialog.component';
import { UrlConstants } from 'src/app/common/constants/url.constants';

@Component({
  selector: 'app-landing-home',
  templateUrl: './landing-home.component.html',
  styleUrls: ['./landing-home.component.scss']
})
export class LandingHomeComponent implements OnInit {

  constructor(private dialog: MatDialog, private router: Router) { }

  ngOnInit(): void {
  }

  signupClicked(): void {
    // const dialogRef = this.dialog.open(SignupDialogComponent, {
    //   data: {},
    //   panelClass: 'filter-popup'
    // });
    this.router.navigate([UrlConstants.SIGN_UP]);
  }

}
