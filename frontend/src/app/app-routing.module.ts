import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AboutUsComponent } from './pages/about-us/about-us.component';
import { CardViewDetailsComponent } from './pages/card-view-details/card-view-details.component';
import { CreateDekkCardComponent } from './pages/create-dekk-card/create-dekk-card.component';
import { CreateEditCardComponent } from './pages/create-edit-dekk/create-edit-card/create-edit-card.component';
import { CreateEditDekkDetailComponent } from './pages/create-edit-dekk/create-edit-dekk-detail/create-edit-dekk-detail.component';
import { CreateEditSubdekkDetailComponent } from './pages/create-edit-dekk/create-edit-subdekk-detail/create-edit-subdekk-detail.component';
import { DekkWithCardsEditViewComponent } from './pages/create-edit-dekk/dekk-with-cards-edit-view/dekk-with-cards-edit-view.component';
import { HomeComponent } from './pages/home/home.component';
import { LandingHomeComponent } from './pages/landing-home/landing-home.component';
import { LoginComponent } from './pages/login/login.component';
import { PageNotFoundComponent } from './pages/page-not-found/page-not-found.component';
import { SearchResultsComponent } from './pages/search-results/search-results.component';
import { SignUpComponent } from './pages/sign-up/sign-up.component';
import { StudyCardComponent } from './pages/study-card/study-card.component';
import { StudySessionComponent } from './pages/study-session/study-session.component';
import { TextEditComponent } from './pages/text-edit/text-edit.component';
import { WhyDekkComponent } from './pages/why-dekk/why-dekk.component';

const routes: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent, pathMatch: 'full',  runGuardsAndResolvers: 'always' },
  { path: 'search-results', component: SearchResultsComponent, pathMatch: 'full' },
  { path: 'card-view-details', component: CardViewDetailsComponent, pathMatch: 'full' },
  { path: 'study-card', component: StudyCardComponent, pathMatch: 'full' },
  { path: 'login', component: LoginComponent, pathMatch: 'full' },
  { path: 'sign-up', component: SignUpComponent, pathMatch: 'full' },
  { path: 'edit', component: TextEditComponent, pathMatch: 'full' },
  { path: 'create', component: CreateEditDekkDetailComponent, pathMatch: 'full' },
  { path: 'create-dekk-card', component: CreateDekkCardComponent, pathMatch: 'full' },
  { path: 'create-subdekk', component: CreateEditSubdekkDetailComponent, pathMatch: 'full' },
  { path: 'dekk-edit-view', component: DekkWithCardsEditViewComponent, pathMatch: 'full' },
  { path: 'card-edit-view', component: CreateEditCardComponent, pathMatch: 'full' },
  { path: 'landing', component: LandingHomeComponent, pathMatch: 'full' },
  { path: 'about', component: AboutUsComponent, pathMatch: 'full' },
  { path: 'why-dekk', component: WhyDekkComponent, pathMatch: 'full' },
  { path: 'study-session', component: StudySessionComponent, pathMatch: 'full' },
  { path: 'page-not-found', component: PageNotFoundComponent, pathMatch: 'full' },
  { path: '**', redirectTo: '/page-not-found' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {onSameUrlNavigation: 'reload'})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
