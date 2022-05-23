import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { UrlConstants } from 'src/app/common/constants/url.constants';
import { CollegeService } from 'src/app/common/services/college.service';
import { HttpClientService } from 'src/app/common/services/http-client.service';
import { UserService } from 'src/app/common/services/user.service';
import { Md5 } from 'ts-md5';

@Component({
  selector: 'app-sign-up',
  templateUrl: './sign-up.component.html',
  styleUrls: ['./sign-up.component.scss']
})
export class SignUpComponent implements OnInit {

  email: string;
  username: string;
  name: string;
  password: string;
  selectedCollege: string;
  signUpError = false;
  loginError = false;
  isLoading = false;

  constructor(private router: Router, 
    public collegeService: CollegeService, 
    private httpClientService: HttpClientService,
    private userService: UserService) { }

  ngOnInit(): void {
  }

  signUp() : void {
    const signUpReq = {
      user_name: this.username,
      full_name: this.name,
      email: this.email,
      password: Md5.hashStr(this.password),
      college: this.selectedCollege
    };
    this.isLoading = true;
    this.httpClientService.postWithoutAuth(UrlConstants.REGISTER_URL, signUpReq)
      .subscribe((response: any) => {
        this.signUpError = false;
        this.login();
    }, (error: any) => { // TODO: Differentiate between errors
      this.signUpError = true;
      this.isLoading = false;
    });
  }

  login(): void {
    const loginReq = {
      email: this.email,
      password: Md5.hashStr(this.password)
    };
    this.httpClientService.postWithoutAuth(UrlConstants.LOGIN_URL, loginReq)
      .subscribe((response: any) => {
        this.loginError = false;
        this.userService.loginSuccessful(response?.auth_token);
        this.router.navigate([UrlConstants.HOME]);
    }, (error: any) => { // TODO: Differentiate between errors
      this.loginError = true;
      this.isLoading = false;
    });
  }
}
