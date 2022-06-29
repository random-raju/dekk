import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { FormControl } from '@angular/forms';
import { MatTabGroup } from '@angular/material/tabs';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { share } from 'rxjs/operators';
import { UrlConstants } from 'src/app/common/constants/url.constants';
import { Dekk } from 'src/app/common/models/dekk';
import { HomeResponse } from 'src/app/common/models/home-response';
import { DekkService } from 'src/app/common/services/dekk-service';
import { HttpClientService } from 'src/app/common/services/http-client.service';
import { StudyService } from 'src/app/common/services/study.service';
import { TagsService } from 'src/app/common/services/tags.service';
import { UserService } from 'src/app/common/services/user.service';
import { CardUtils } from 'src/app/common/utils/card.utils';
import { DekkUtils } from 'src/app/common/utils/dekk-utils';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit, OnDestroy {
  @ViewChild("dekkTabs", { static: false }) dekkTabs: MatTabGroup;

  dekks: Dekk[] = [];
  personalDekks: Dekk[] = [];
  selectedMasterDekkId: string|null = null;
  selectedMasterDekk: any = CardUtils.getWaitCard();
  isLoading: boolean = true;
  routeListener: any;
  locationListener: any;
  dekkLoadListener: any;
  homeLoadListener: any;
  tabIndex = 0;

  constructor(private httpClientService: HttpClientService, 
    private studyService: StudyService, 
    private userService: UserService,
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private dekkService: DekkService,
    private tagsService: TagsService) {
      // if (!this.userService.loggedIn) {
      //   this.router.navigate([UrlConstants.LANDING]);
      // }
      this.routeListener = this.router.events.subscribe((event) => {
        this.isLoading = true;
        if (event instanceof NavigationEnd) {
          if (!this.userService.loggedIn) {
            this.router.navigate([UrlConstants.LANDING]);
            return;
          }
          this.locationListener = this.activatedRoute.queryParams.subscribe(params => {
            if (params.id) {
              this.selectedMasterDekkId = params.id;
              this.initialise();
            } else {
              this.selectedMasterDekkId = null;
              this.initialise();
            }
          });
          this.locationListener.pipe(share());
        }
      });
  }

  ngOnInit(): void {
    // this.initialise();
    // this.dekkTabs.focusTab(1);
    // this.dekkTabs.selectedIndex = (this.dekkTabs.selectedIndex ?? 0 + 1) % this.dekkTabs._tabs.length;
  }

  ngOnDestroy(): void {
    this.routeListener?.unsubscribe();
    this.locationListener?.unsubscribe();
    this.dekkLoadListener?.unsubscribe();
    this.homeLoadListener?.unsubscribe();
  }

  initialise(): void {
    this.isLoading = true;
    this.tagsService.loadTags();
    if (this.selectedMasterDekkId) {
      this.homeLoadListener = this.httpClientService.get(UrlConstants.HOME_URL, []).subscribe((response: HomeResponse) => {
        this.personalDekks = response && response.user_dekks ? response.user_dekks : [];
      });

      this.dekkLoadListener = this.dekkService.loadDekkDetails(this.selectedMasterDekkId).subscribe((response: any) => {
        this.dekks = [];
        if (response) {
          this.selectedMasterDekk = response.filter((dekk: any) => dekk.dekk_id === this.selectedMasterDekkId)[0];
          if (this.selectedMasterDekk.sub_dekks) {
            this.selectedMasterDekk.sub_dekks.forEach((subDekk: any) => {
              this.dekks.push({
                total_cards: subDekk.cards_count,
                tag_name: subDekk.tag_name,
                tag_id: subDekk.tag_id,
                field: subDekk.tag_name,
                is_owner: subDekk.is_owner
              });
            });

            // temp - TODO remove
            // this.dekks = this.dekks.map((dekk: Dekk) => { dekk.is_owner = true; return dekk; });
          }
        }

        if (this.dekks.length === 0) {
          this.studySessionDekk(this.selectedMasterDekkId!);
        }

        setTimeout(() => {
          this.isLoading = false; 
          console.log(this.dekkTabs._tabs);
        }, 500);
      });
    } else {
      this.dekkLoadListener = this.httpClientService.get(UrlConstants.HOME_URL, []).subscribe((response: HomeResponse) => {
        this.dekks = response && response.dekk_stats ? response.dekk_stats : [];
        const curatedDekkIds = this.dekks.map((dekk: Dekk) => dekk.tag_id);
        this.personalDekks = response && response.user_dekks ? 
          response.user_dekks.filter((dekk: Dekk) => !curatedDekkIds.includes(dekk.tag_id)) : [];
        this.selectedMasterDekk = DekkUtils.getEmptyDekkMetadata();

        //temp - TODO remove
        // this.dekks = this.dekks.map((dekk: Dekk) => { dekk.is_owner = true; return dekk; });
        // this.personalDekks = this.personalDekks.map((dekk: Dekk) => { dekk.is_owner = true; return dekk; });

        setTimeout(() => {
          this.isLoading = false; 
        }, 500);
      });
    }
  }

  selectDekk(dekkId: string): void {
    if (!this.selectedMasterDekkId) {
      this.router.navigateByUrl('/', {skipLocationChange: true}).then(() => {
        this.router.navigate([UrlConstants.HOME], {queryParams: { id: dekkId }});
      });
    } else {
      this.selectSubDekk(dekkId);
    }
  }

  selectSubDekk(dekkId: string): void {
    this.studySessionDekk(dekkId);
  }

  studyDekk(dekkId: string): void {
    this.studyService.selectedIds = [dekkId];
    this.studyService.maxCards = -1;
    this.router.navigate([UrlConstants.STUDY_CARD]);
  }

  studySessionDekk(dekkId: string): void {
    this.router.navigateByUrl(UrlConstants.STUDY_SESSION, {state: { selectedDekkId: dekkId }});
  }

  editDekk(dekk: any): void {
    this.router.navigate([UrlConstants.DEKK_EDIT_VIEW], {queryParams: { id: dekk.dekk_id ?? dekk.tag_id }});
  }

  createSubdekk(): void {
    this.router.navigate([UrlConstants.CREATE_SUBDEKK], {queryParams: { id: this.selectedMasterDekkId }});
  }
}
