import { GoogleLoginProvider, SocialAuthService, SocialUser } from 'angularx-social-login';
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

  googleUser: SocialUser = new SocialUser;

  constructor(private router: Router,
    private httpClientService: HttpClientService,
    private userService: UserService,
    private authService: SocialAuthService) {
  }

  ngOnInit(): void {
  }

  login(): void {
    const loginReq = {
      email: this.email,
      password: Md5.hashStr(this.password),
      verification_code: 12345
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

  loginGoogle(): void {
    this.authService.signIn(GoogleLoginProvider.PROVIDER_ID);
    this.authService.authState.subscribe((user: any) => {
      this.googleUser = user;
      console.log(this.googleUser);
      const loginUser = {
        email: this.googleUser.email,
        givenName: this.googleUser.firstName,
        familyName: this.googleUser.lastName,
        imageUrl: this.googleUser.photoUrl,
        googleId: this.googleUser.id,
        name: this.googleUser.name
      };
      this.httpClientService.postWithoutAuth(UrlConstants.GOOGLE_REGISTER_LOGIN_URL, loginUser)
        .subscribe((response: any) => {
          this.loginError = false;
          this.userService.loginSuccessful(response?.auth_token);
          this.router.navigate([UrlConstants.HOME]);
      }, (error: any) => { // TODO: Differentiate between errors
        this.loginError = true;
        this.isLoading = false;
      });
    });
  }

  logoutGoogle(): void {
    this.authService.signOut();
  }
}
