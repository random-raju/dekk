import { Component, Directive, Input, OnChanges, OnInit } from '@angular/core';
import { Card } from '../../../models/card';
import { StudyService } from '../../../services/study.service';
import { CardUtils } from '../../../utils/card.utils';
import rxmq from 'rxmq';
import { Subject } from 'rxjs';
import { MessageConstants } from 'src/app/common/constants/message.constants';
import { MatDialog } from '@angular/material/dialog';
import { RatingDialogComponent } from '../../rating-dialog/rating-dialog.component';
import { ImgDialogComponent } from '../../img-dialog/img-dialog.component';

@Component({
  selector: 'app-card-front',
  templateUrl: './card-front.component.html',
  styleUrls: ['./card-front.component.scss']
})
export class CardFrontComponent implements OnInit, OnChanges {

  @Input()
  card: Card;

  content: string;
  dekkRating: number;
  dekkFeedback: string;
  firstImageLoading: boolean;
  secondImageLoading: boolean;

  flipToBackObservable: Subject<any>;

  constructor(public studyService: StudyService, public dialog: MatDialog) {
    this.flipToBackObservable = rxmq.channel(MessageConstants.STUDY_CHANNEL)
      .subject(MessageConstants.STUDY_FLIP_TO_BACK_ACTION);
  }

  ngOnInit(): void {
  }

  ngOnChanges(): void {
    // this.content = this.studyService.getUnhighlightedCardBack();
    this.firstImageLoading = true;
    this.secondImageLoading = true;
    this.content = this.studyService.getHighlightedCardFront();
  }

  getCardDekk(): string {
    return CardUtils.getCardCategoryText(this.card);
  }

  flipToBack(): void {
    this.flipToBackObservable.next({
      title: 'flipToBack',
      text: 'Flip to back',
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
    // return "https://drive.google.com/uc?export=view&id=1LY4GtGy3CHvgm1QKYi1JhTvqQffLmn0w"
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
