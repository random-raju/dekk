import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { ErrorDialogComponent } from 'src/app/common/components/error-dialog/error-dialog.component';
import { RatingDialogComponent } from 'src/app/common/components/rating-dialog/rating-dialog.component';
import { PopupConstants } from 'src/app/common/constants/popup.constants';
import { UrlConstants } from 'src/app/common/constants/url.constants';
import { Card } from 'src/app/common/models/card';
import { DekkMetadata } from 'src/app/common/models/dekk-metadata';
import { DekkService } from 'src/app/common/services/dekk-service';
import { StudyService } from 'src/app/common/services/study.service';
import { CardUtils } from 'src/app/common/utils/card.utils';
import { DekkUtils } from 'src/app/common/utils/dekk-utils';

@Component({
  selector: 'app-dekk-with-cards-edit-view',
  templateUrl: './dekk-with-cards-edit-view.component.html',
  styleUrls: ['./dekk-with-cards-edit-view.component.scss']
})
export class DekkWithCardsEditViewComponent implements OnInit {

  routeListener: Subscription;

  displayedColumns = ["card", "preview", "action"];
  dekkRating: number;
  dekkFeedback: string;
  currentDekkId: string;
  currentDekk: DekkMetadata = DekkUtils.getEmptyDekkMetadata();
  isLoading: boolean = true;

  constructor(private router: Router, private activatedRoute: ActivatedRoute, public dialog: MatDialog, private dekkService: DekkService, private studyService: StudyService) {
    this.routeListener = this.router.events.subscribe((event: any) => {
      this.isLoading = true;
      if (event instanceof NavigationEnd) {
        const currentUrl = event.url.split('?')[0];
        if (currentUrl === UrlConstants.DEKK_EDIT_VIEW) {
          this.activatedRoute.queryParams.subscribe((params: any) => {
            if (params.id) {
              this.currentDekkId = params.id;
              this.dekkService.loadDekkMetadataByDekkId(this.currentDekkId!).subscribe((dekkMetadata: DekkMetadata) => {
                this.currentDekk = dekkMetadata;
                setTimeout(() => {
                  this.isLoading = false;
                }, 500);
              }, (error: any) => {
                this.handleDekkLoadError();
              });
            } else {
              this.handleDekkLoadError();
            }
          });
        }
      }
    });
  }

  handleDekkLoadError(): void {
    this.handleDekkError(PopupConstants.DEKK_METADATA_LOAD_ERROR);
  }

  handleDekkError(msg: string): void {
    const dialogRef = this.dialog.open(ErrorDialogComponent, {
      data: {
          msg
      }
    });
    dialogRef.afterClosed().subscribe(result => {
        console.log('The dialog was closed: ', result);
    });
  }

  ngOnInit(): void {
  }

  ngOnDestroy(): void {
    this.routeListener.unsubscribe();
  }

  getCardCategory(): string {
    return "Personal";
  }

  addCard(): void {
    this.router.navigate([UrlConstants.CARD_EDIT_VIEW], {queryParams: { dekk_id: this.currentDekkId }});
  }

  rateDialog(): void {
    const dialogRef = this.dialog.open(RatingDialogComponent, {
      data: {
        dekk_id: 'dekk1',
        current_rating: 3
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      this.dekkRating = result.current_rating;
      this.dekkFeedback = result.feedback;
      console.log('The dialog was closed: ', result);
    });
  }

  editDekk(): void {
    // this.isLoading = true;
    this.router.navigate([UrlConstants.CREATE], {queryParams: { id: this.currentDekkId }});
  }

  editCard(cardId: string): void {
    // this.isLoading = true;
    this.router.navigate([UrlConstants.CARD_EDIT_VIEW], {queryParams: { id: cardId, dekk_id: this.currentDekkId }});
  }

  deleteCard(cardId: string): void {
    this.isLoading = true;
    this.dekkService.deleteCard(cardId).subscribe((response: any) => {
      this.dekkService.loadDekkMetadataByDekkId(this.currentDekkId!).subscribe((dekkMetadata: DekkMetadata) => {
        this.currentDekk = dekkMetadata;
        setTimeout(() => {
          this.isLoading = false;
        }, 500);
      }, (error: any) => {
        this.handleDekkLoadError();
      });
    }, (error: any) => {
      this.handleDekkError(PopupConstants.DEKK_METADATA_DELETE_ERROR);
    });
  }

  studyDekk(): void {
    this.studyService.selectedIds = [this.currentDekkId];
    this.router.navigate([UrlConstants.STUDY_CARD]);
  }

  getPreview(element: any) {
    return element.content_on_front;
  }
}
