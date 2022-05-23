import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { UrlConstants } from 'src/app/common/constants/url.constants';
import { HttpClientService } from 'src/app/common/services/http-client.service';
import { UserService } from 'src/app/common/services/user.service';
import { Md5 } from 'ts-md5';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

  email: string;
  password: string;
  loginError = false;
  isLoading = false;

  constructor(private router: Router,
    private httpClientService: HttpClientService,
    private userService: UserService) { }

  ngOnInit(): void {
  }

  login(): void {
    const loginReq = {
      email: this.email,
      password: Md5.hashStr(this.password)
    };
    this.isLoading = true
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
