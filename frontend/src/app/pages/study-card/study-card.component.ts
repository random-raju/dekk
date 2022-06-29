import { Component, Input, OnDestroy, OnInit } from "@angular/core";
import { Event, NavigationEnd, Router } from "@angular/router";
import { Subscription } from "rxjs";
import { Card } from "src/app/common/models/card";
import { StudyService } from "src/app/common/services/study.service";
import { CardUtils } from "src/app/common/utils/card.utils";
import { trigger, state, style, transition, animate } from '@angular/animations';
import rxmq from 'rxmq';
import { MessageConstants } from "src/app/common/constants/message.constants";
import { PunsConstants } from "src/app/common/constants/puns.constants";
import { PopupConstants } from 'src/app/common/constants/popup.constants';
import { MatDialog } from "@angular/material/dialog";
import { ErrorDialogComponent } from 'src/app/common/components/error-dialog/error-dialog.component';

@Component({
  selector: 'app-study-card',
  styleUrls: ['./study-card.component.scss'],
  templateUrl: './study-card.component.html',
  animations: [
    trigger('flipState', [
      state('active', style({
        transform: 'rotateY(180deg)'
      })),
      state('inactive', style({
        transform: 'rotateY(0deg)'
      })),
      transition('active => inactive', animate('500ms ease-out')),
      transition('inactive => active', animate('500ms ease-in'))
    ])
  ]
})
export class StudyCardComponent implements OnInit, OnDestroy {
  
  card: Card = CardUtils.getWaitCard();

  visibleFront = true;
  flip: string = 'inactive';

  flipToFrontSubscription: Subscription;
  flipToBackSubscription: Subscription;
  rightWrongSubscription: Subscription;

  // For loading screen
  // for initial load - isNewDekkLoaded && isMinLoadTimeElapsed
  isNewDekkLoaded = false; // for initial load
  isMinLoadTimeElapsed = false; // for initial load
  isLoading = false; // for general loads

  routeListener: any;

  constructor(private router: Router, public studyService: StudyService, private dialog: MatDialog) {}

  ngOnInit() {
    this.isLoading = true;
    this.isNewDekkLoaded = false;
    this.isMinLoadTimeElapsed = false;
    setTimeout(() => {
      this.isMinLoadTimeElapsed = true;
    }, 500);
    
    this.studyService.loadNewDekk().subscribe(response => {
      this.card = this.studyService.getCurrentCard();
      if (this.studyService.dekkCards.length === 0) {
        setTimeout(() => {
          const dialogRef = this.dialog.open(ErrorDialogComponent, {
            data: {
                msg: PopupConstants.NO_CARDS_ERROR
            }
          });
          dialogRef.afterClosed().subscribe(result => {
              console.log('The dialog was closed: ', result);
          }); 
        });
      } else {
        setTimeout(() => {
          this.isNewDekkLoaded = true;
          this.isLoading = false;
        }, 500);
      }
    });

    this.routeListener = this.router.events.subscribe((event: Event) => {
      if (event instanceof NavigationEnd) {
        this.visibleFront = true;
        this.flip = 'inactive';
        this.card = this.studyService.getCurrentCard();
      }
    });

    this.flipToFrontSubscription = rxmq.channel(MessageConstants.STUDY_CHANNEL)
      .observe(MessageConstants.STUDY_FLIP_TO_FRONT_ACTION)
      .subscribe(() => { this.flipToFront(); });

    this.flipToBackSubscription = rxmq.channel(MessageConstants.STUDY_CHANNEL)
      .observe(MessageConstants.STUDY_FLIP_TO_BACK_ACTION)
      .subscribe(() => { this.flipToBack(); });

    this.rightWrongSubscription = rxmq.channel(MessageConstants.RIGHT_WRONG_CHANNEL)
      .observe(MessageConstants.RIGHT_ACTION)
      .subscribe(() => { this.countRightWrongStats(MessageConstants.RIGHT_ACTION); });

    this.rightWrongSubscription = rxmq.channel(MessageConstants.RIGHT_WRONG_CHANNEL)
      .observe(MessageConstants.WRONG_ACTION)
      .subscribe(() => { this.countRightWrongStats(MessageConstants.WRONG_ACTION); });
  }

  ngOnDestroy() {
    this.routeListener.unsubscribe();
    this.rightWrongSubscription.unsubscribe();
  }

  getCardCategory(): string {
    // return CardUtils.getCardCategoryText(this.card);
    return this.card.title;
  }

  flipToFront() {
    this.toggleFlip();
    setTimeout(() => {this.visibleFront = true;}, 250);
  }

  flipToBack() {
    this.toggleFlip();
    if (!!this.card?.card_id) {
      this.studyService.markCardAsRead(this.card);
    }
    setTimeout(() => {this.visibleFront = false;}, 250);
  }

  isCardFrontVisible(): boolean {
    return this.visibleFront;
  }

  toggleFlip() {
    this.flip = (this.flip === 'inactive') ? 'active' : 'inactive';
  }

  getNextCard(): void {
    this.animateToNextCard();
    // this.studyService.goToNextCard();
    this.studyService.getNextCard().subscribe((cardResponse: any) => {
      if (cardResponse) {
        this.card = cardResponse;
      }
    });
  }

  getPreviousCard(): void {
    this.animateToNextCard();
    this.card = this.studyService.getPreviousCard();
  }

  animateToNextCard(): void {
    this.visibleFront = true;
    if (this.flip === 'active') {
      this.toggleFlip();
    }
  }

  countRightWrongStats(action: string): void {
    if (action === MessageConstants.RIGHT_ACTION) {
      this.studyService.markGotCardRight();
    }
  }
}
