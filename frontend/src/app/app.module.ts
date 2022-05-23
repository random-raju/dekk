import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatCardModule } from "@angular/material/card";
import { MatListModule } from "@angular/material/list";
import { MatChipsModule } from "@angular/material/chips";
import { MatExpansionModule } from "@angular/material/expansion";
import { MatProgressBarModule } from "@angular/material/progress-bar";
import { MatTooltipModule } from "@angular/material/tooltip";
import { MatSelectModule } from '@angular/material/select';
import { MatTableModule } from '@angular/material/table';
import { MatDialogModule } from '@angular/material/dialog';
import { MatMenuModule } from '@angular/material/menu';
import { MatDividerModule } from '@angular/material/divider';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatTabsModule } from '@angular/material/tabs';

import { NgMatSearchBarModule } from 'ng-mat-search-bar';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SearchResultsComponent } from './pages/search-results/search-results.component';
import { SearchResultComponent } from './common/components/search-result/search-result.component';
import { HttpClientModule } from '@angular/common/http';
import { CardViewDetailsComponent } from './pages/card-view-details/card-view-details.component';
import { CardFrontComponent } from './common/components/card/card-front/card-front.component';
import { StudyCardComponent } from './pages/study-card/study-card.component';
import { CardBackComponent } from './common/components/card/card-back/card-back.component';
import { ScrollingModule } from '@angular/cdk/scrolling';
import { LoginComponent } from './pages/login/login.component';
import { SignUpComponent } from './pages/sign-up/sign-up.component';
import { HomeComponent } from './pages/home/home.component';
import { TextEditComponent } from './pages/text-edit/text-edit.component';
import { EditorModule } from '@tinymce/tinymce-angular';
import { StudyMsgDialogComponent } from './common/components/study-msg-dialog/study-msg-dialog.component';
import { CreateEditDekkDetailComponent } from './pages/create-edit-dekk/create-edit-dekk-detail/create-edit-dekk-detail.component';
import { DekkWithCardsEditViewComponent } from './pages/create-edit-dekk/dekk-with-cards-edit-view/dekk-with-cards-edit-view.component';
import { CreateEditCardComponent } from './pages/create-edit-dekk/create-edit-card/create-edit-card.component';
import { SignupLoginComponent } from './pages/signup-login/signup-login.component';
import { RatingDialogComponent } from './common/components/rating-dialog/rating-dialog.component';
import { LandingHomeComponent } from './pages/landing-home/landing-home.component';
import { LoginDialogComponent } from './common/components/login-dialog/login-dialog.component';
import { SignupDialogComponent } from './common/components/signup-dialog/signup-dialog.component';
import { LayoutModule } from '@angular/cdk/layout';
import { MatOptionModule } from '@angular/material/core';
import { CdkColumnDef } from '@angular/cdk/table';
import { BarRatingModule } from 'ngx-bar-rating';
import { AboutUsComponent } from './pages/about-us/about-us.component';
import { WhyDekkComponent } from './pages/why-dekk/why-dekk.component';
import { StudySessionComponent } from './pages/study-session/study-session.component';
import { ImgDialogComponent } from './common/components/img-dialog/img-dialog.component';
import { LoadingComponent } from './common/components/loading/loading.component';
import { ErrorDialogComponent } from './common/components/error-dialog/error-dialog.component';
import { MsgDialogComponent } from './common/components/msg-dialog/msg-dialog.component';
import { CreateEditSubdekkDetailComponent } from './pages/create-edit-dekk/create-edit-subdekk-detail/create-edit-subdekk-detail.component';
import { NgxMatSelectSearchModule } from 'ngx-mat-select-search';
import { PageNotFoundComponent } from './pages/page-not-found/page-not-found.component';
import { CreateDekkCardComponent } from './pages/create-dekk-card/create-dekk-card.component';
// import { TextInputHighlightModule } from 'angular-text-input-highlight';

@NgModule({
  declarations: [
    AppComponent,
    SearchResultComponent,
    SearchResultsComponent,
    CardViewDetailsComponent,
    CardFrontComponent,
    CardBackComponent,
    StudyCardComponent,
    LoginComponent,
    SignUpComponent,
    HomeComponent,
    TextEditComponent,
    StudyMsgDialogComponent,
    TextEditComponent,
    CreateEditDekkDetailComponent,
    DekkWithCardsEditViewComponent,
    CreateEditCardComponent,
    SignupLoginComponent,
    RatingDialogComponent,
    LandingHomeComponent,
    LoginDialogComponent,
    SignupDialogComponent,
    AboutUsComponent,
    WhyDekkComponent,
    StudySessionComponent,
    ImgDialogComponent,
    LoadingComponent,
    ErrorDialogComponent,
    MsgDialogComponent,
    CreateEditSubdekkDetailComponent,
    PageNotFoundComponent,
    CreateDekkCardComponent,
  ],
  imports: [
    AppRoutingModule,
    BrowserModule,
    BrowserAnimationsModule,
    FormsModule,
    LayoutModule,
    ReactiveFormsModule,
    ScrollingModule,
    HttpClientModule,
    NgMatSearchBarModule,
    EditorModule,
    BarRatingModule,
    NgxMatSelectSearchModule,
    // TextInputHighlightModule,
    MatButtonModule,
    MatSlideToggleModule,
    MatToolbarModule,
    MatIconModule,
    MatInputModule,
    MatSidenavModule,
    MatCardModule,
    MatFormFieldModule,
    MatListModule,
    MatChipsModule,
    MatExpansionModule,
    MatProgressBarModule,
    MatTooltipModule,
    MatOptionModule,
    MatSelectModule,
    MatTableModule,
    MatDialogModule,
    MatMenuModule,
    MatDividerModule,
    MatCheckboxModule,
    MatAutocompleteModule,
    MatTabsModule
  ],
  providers: [
    CdkColumnDef
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
