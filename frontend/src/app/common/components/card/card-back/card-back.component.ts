import { Component, Input, OnChanges, OnInit } from '@angular/core';
import { Subject } from 'rxjs';
import { Card } from 'src/app/common/models/card';
import { StudyService } from 'src/app/common/services/study.service';
import rxmq from 'rxmq';
import { MessageConstants } from 'src/app/common/constants/message.constants';
import { CardUtils } from 'src/app/common/utils/card.utils';
import { MatDialog } from '@angular/material/dialog';
import { RatingDialogComponent } from '../../rating-dialog/rating-dialog.component';
import { ImgDialogComponent } from '../../img-dialog/img-dialog.component';

@Component({
  selector: 'app-card-back',
  templateUrl: './card-back.component.html',
  styleUrls: ['./card-back.component.scss']
})
export class CardBackComponent implements OnInit, OnChanges {

  @Input()
  card: Card;

  content: string;
  dekkRating: number;
  dekkFeedback: string;
  firstImageLoading: boolean;
  secondImageLoading: boolean;

  flipToFrontObservable: Subject<any>;

  rightObervable: Subject<any>;
  wrongObervable: Subject<any>;

  constructor(public studyService: StudyService, public dialog: MatDialog) {
    this.flipToFrontObservable = rxmq.channel(MessageConstants.STUDY_CHANNEL)
      .subject(MessageConstants.STUDY_FLIP_TO_FRONT_ACTION);
  }

  ngOnInit(): void {
    this.rightObervable = rxmq.channel(MessageConstants.RIGHT_WRONG_CHANNEL)
      .subject(MessageConstants.RIGHT_ACTION);
    this.wrongObervable = rxmq.channel(MessageConstants.RIGHT_WRONG_CHANNEL)
      .subject(MessageConstants.WRONG_ACTION);
  }

  ngOnChanges(): void {
    // this.content = this.studyService.getUnhighlightedCardBack();
    this.firstImageLoading = true;
    this.secondImageLoading = true;
    this.content = this.studyService.getHighlightedCardBack();
  }

  getCardDekk(): string {
    return CardUtils.getCardCategoryText(this.card);
  }

  highlight(): void {
    this.content = this.studyService.getHighlightedCardBack();
  }

  flipToFront(): void {
    this.flipToFrontObservable.next({
      title: 'flipToFront',
      text: 'Flip to front',
    });
  }

  rateDialog(): void {
    const dialogRef = this.dialog.open(RatingDialogComponent, {
      data: {
        dekk_id: 'dekk1',
        card_id: this.card.card_id,
        current_rating: 3
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.dekkRating = result.current_rating;
        this.dekkFeedback = result.feedback;
        console.log('The dialog was closed: ', this.dekkRating, this.dekkFeedback);
      }
    });
  }

  gotItRight(): void {
    if (!this.card.rightWrongMarked) {
      this.rightObervable.next({
        title: 'Right',
        text: 'Right',
      });
      this.card.rightWrongMarked = true;
    }
  }

  gotItWrong(): void {
    if (this.card.rightWrongMarked) {
      this.wrongObervable.next({
        title: 'Wrong',
        text: 'Wrong',
      });
    }
  }

  openImg(src: string|null): void {
    const dialogRef = this.dialog.open(ImgDialogComponent, {
      data: {
          msg: src ?? ''
      }
    });
    dialogRef.afterClosed().subscribe(result => {
        console.log('The dialog was closed: ', result);
    });
  }

  getFirstImageSrc(): string|null {
    return this.studyService.getCurrentCard().image_links[0];
  }

  getSecondImageSrc(): string|null {
    return this.studyService.getCurrentCard().image_links[1];
  }

  firstImageLoaded(): void {
    this.firstImageLoading = false;
  }

  secondImageLoaded(): void {
    this.secondImageLoading = false;
  }

  isNoImages(): boolean {
    return this.studyService.getCurrentCard().image_links?.length === 0;
  }

  bookmarkToggle(): void {
    if (this.card.is_bookmarked) {
      this.studyService.unbookmark(this.card);
    } else {
      this.studyService.bookmark(this.card);
    }
  }
}
