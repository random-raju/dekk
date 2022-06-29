import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { UrlConstants } from "../constants/url.constants";
import { Card } from "../models/card";
import { HttpClientService } from "./http-client.service";
import * as _ from 'lodash';
import { MatDialog } from "@angular/material/dialog";
import { PopupConstants } from "../constants/popup.constants";
import { StudyMsgDialogComponent } from "../components/study-msg-dialog/study-msg-dialog.component";
import { CardUtils } from "../utils/card.utils";

@Injectable({
    providedIn: 'root',
})
export class StudyService {

    dekkCards: Card[];
    currentCardIndex: number = -1; // Invalid card case
    currentSessionCardIds: string[] = [];
    isDekkComplete: boolean = false;
    dekkParams: any;
    selectedIds: string[] = ['invalid'];
    totalCardsStudied = 0;
    rightCards = 0;
    maxCards = -1;

    constructor(private httpClientService: HttpClientService, public dialog: MatDialog) {}

    loadNewDekk(): Observable<any> { 
        this.dekkCards = [];
        this.isDekkComplete = false;
        this.currentCardIndex = -1;
        this.totalCardsStudied = 0;
        this.rightCards = 0;
        this.currentSessionCardIds = [];

        this.dekkParams = {
            ids: this.selectedIds,
            offset: 0,
            cards_count: this.maxCards > 0 ? this.maxCards : CardUtils.STUDY_SESSION_DEFAULT_MAX_NUM_OF_CARDS
        };

        const dekkLoadObservable = this.httpClientService.post(UrlConstants.CARDS_FROM_DEKK_ID_URL, this.dekkParams);

        this.handleCardsLoad(dekkLoadObservable);

        return dekkLoadObservable;
    }

    getNextCard(): Observable<any> {
        const nextCardObservable = new Observable((observer) => {
            // If we somehow reached the last card and dekk is not yet over, return loading and load next cards
            if (!this.isDekkComplete && this.currentCardIndex === this.dekkCards?.length - 1) {
                this.loadMoreCards()?.subscribe(() => {
                    if (this.currentCardIndex < this.dekkCards?.length - 1) {
                        ++ this.currentCardIndex;
                        if (!this.dekkCards[this.currentCardIndex].visited) {
                            ++ this.totalCardsStudied;
                        }
                        this.dekkCards[this.currentCardIndex].visited = true;
                        observer.next(this.dekkCards[this.currentCardIndex]);
                    } else {
                        let dialogRef;
                        let dialogMsg = PopupConstants.DEKK_COMPLETE_MSG;
                        let rightPercentage = 0;
                        if (this.totalCardsStudied > 0 && this.rightCards > 0) {
                            rightPercentage = (this.rightCards / this.totalCardsStudied) * 100;
                        }
                        rightPercentage = parseInt(rightPercentage.toString());
                        dialogMsg += `.<br> You got ${rightPercentage}% of the cards right.`;
                        if (rightPercentage > 50) {
                            dialogMsg += '<br>Great job!';
                        } else {
                            dialogMsg += '<br>Keep working hard!';
                        }
                        dialogRef = this.dialog.open(StudyMsgDialogComponent, {
                            data: {
                                msg: dialogMsg
                            }
                        });
                        dialogRef.afterClosed().subscribe(result => {
                            console.log('The dialog was closed: ', result);
                        });
                        observer.next(this.dekkCards[this.currentCardIndex]); // return same card when dekk is over
                    }
                });
            }
            // If there are 5 cards left and the dekk is not yet over, load the next set preemptively
            else if (!this.isDekkComplete && this.currentCardIndex === this.dekkCards?.length - 5) {
                this.loadMoreCards();
                ++ this.currentCardIndex;
                if (!this.dekkCards[this.currentCardIndex].visited) {
                    ++ this.totalCardsStudied;
                }
                this.dekkCards[this.currentCardIndex].visited = true;
                observer.next(this.dekkCards[this.currentCardIndex]);
            } 
            // TODO? add a check here for currentCardIndex at the end but next card set not yet loaded
            else if (this.isDekkComplete && this.currentCardIndex === this.dekkCards.length - 1) {
                let dialogRef;
                let dialogMsg = PopupConstants.DEKK_COMPLETE_MSG;
                let rightPercentage = 0;
                if (this.totalCardsStudied > 0 && this.rightCards > 0) {
                    rightPercentage = (this.rightCards / this.totalCardsStudied) * 100;
                }
                rightPercentage = parseInt(rightPercentage.toString());
                dialogMsg += `.<br> You got ${rightPercentage}% of the cards right.`;
                if (rightPercentage > 50) {
                    dialogMsg += '<br>Great job!';
                } else {
                    dialogMsg += '<br>Keep working hard!';
                }
                dialogRef = this.dialog.open(StudyMsgDialogComponent, {
                    data: {
                        msg: dialogMsg
                    }
                });
                dialogRef.afterClosed().subscribe(result => {
                    console.log('The dialog was closed: ', result);
                });
                observer.next(this.dekkCards[this.currentCardIndex]); // return same card when dekk is over
            } else {
                this.currentCardIndex = this.currentCardIndex < 0 ? 0 : this.currentCardIndex + 1;
                if (!this.dekkCards[this.currentCardIndex].visited) {
                    ++ this.totalCardsStudied;
                }
                this.dekkCards[this.currentCardIndex].visited = true;
                observer.next(this.dekkCards[this.currentCardIndex]);
            }
        });
        return nextCardObservable;
    }

    getPreviousCard(): Card {
        if (this.currentCardIndex > 0) {
            --this.currentCardIndex;
            return this.dekkCards[this.currentCardIndex];
        } else {
            const dialogRef = this.dialog.open(StudyMsgDialogComponent, {
                data: {
                    msg: PopupConstants.DEKK_BEGINNING_MSG
                }
            });
            dialogRef.afterClosed().subscribe(result => {
                console.log('The dialog was closed: ', result);
            });
            return this.dekkCards[this.currentCardIndex];
        }
    }

    loadMoreCards(): Observable<any> {
        this.dekkParams.offset = this.dekkCards.length
        
        const nextLoadObservable = this.httpClientService.post(UrlConstants.CARDS_FROM_DEKK_ID_URL, this.dekkParams);

        this.handleCardsLoad(nextLoadObservable);

        return nextLoadObservable;
    }

    private handleCardsLoad(cardLoadObservable: Observable<any>): void {
        cardLoadObservable.subscribe((response: any) => {
            this.dekkParams.session_id = this.dekkParams.session_id ? this.dekkParams.session_id : response?.session_id;
            if (!response) {
                const dialogRef = this.dialog.open(StudyMsgDialogComponent, {
                    data: {
                        msg: PopupConstants.CARD_LOAD_ERROR
                    }
                });
            
                dialogRef.afterClosed().subscribe(result => {
                    console.log('The dialog was closed: ', result);
                });
            } else if (response.total_cards_given < CardUtils.OFFSET_LOAD_NUM_OF_CARDS) { // this means the dekk is over at/after this point
                this.isDekkComplete = true;
                response.cards.forEach((card: Card) => {
                    if (this.currentSessionCardIds.indexOf(card.card_id) === -1) {
                        this.dekkCards.push(card);
                        this.currentSessionCardIds.push(card.card_id);
                    }
                });
                // this.dekkCards = this.dekkCards.concat(response.cards);
            } else {
                // this.dekkCards = this.dekkCards.concat(response.cards);
                response.cards.forEach((card: Card) => {
                    if (this.currentSessionCardIds.indexOf(card.card_id) === -1) {
                        this.dekkCards.push(card);
                        this.currentSessionCardIds.push(card.card_id);
                    }
                });
            }

            if (this.maxCards >= 0 && this.dekkCards.length >= this.maxCards) {
                this.isDekkComplete = true;
            }

            // increment card index if possible
            this.currentCardIndex = this.dekkCards.length > 0 
                && this.currentCardIndex < this.dekkCards.length - 1 ? this.currentCardIndex + 1 : this.currentCardIndex;
        }, (error: any) => {
            const dialogRef = this.dialog.open(StudyMsgDialogComponent, {
                data: {
                    msg: PopupConstants.CARD_LOAD_ERROR
                }
            });
        
            dialogRef.afterClosed().subscribe(result => {
                console.log('The dialog was closed: ', result);
            });
        });
    }

    getUnhighlightedCardFront(): string {
        if (this.currentCardIndex < 0) {
            return 'Invalid card';
        }
        return this.getUnhighlightedContent(this.dekkCards[this.currentCardIndex]?.content_on_front);
    }

    getUnhighlightedCardBack(): string {
        if (this.currentCardIndex < 0) {
            return 'Invalid card';
        }
        return this.getUnhighlightedContent(this.dekkCards[this.currentCardIndex]?.content_on_back);
    }

    private getUnhighlightedContent(content: string): string {
        if (!content) {
            return '';
        }

        let index = content.indexOf('*');
        while (index >= 0) {
            content = content.substring(0, index) + content.substring(index + 1);
            index = content.lastIndexOf('*');
        }
        while (content.indexOf('\n') >= 0) {
            content = content.replace('\n', '<br />');
        }
        return content;
    }

    getHighlightedCardFront(): string {
        return this.getHighlightedContent(this.dekkCards[this.currentCardIndex]?.content_on_front);
    }

    // TBD: should view card be called here? Like when the card is flipped.
    getHighlightedCardBack(): string {
        return this.getHighlightedContent(this.dekkCards[this.currentCardIndex]?.content_on_back);
    }

    public getHighlightedContent(content: string): string {
        if (!content) {
            return '';
        }
        
        let isEven = true;
        let index = content.lastIndexOf('*');
        while (index >= 0) {
            if (isEven) {
                content = content.substring(0, index) + '</mark>' + content.substring(index + 1);
            } else {
                content = content.substring(0, index) + '<mark>' + content.substring(index + 1);
            }
            isEven = !isEven;
            index = content.lastIndexOf('*');
        }
        while (content.indexOf('\n') >= 0) {
            content = content.replace('\n', '<br />');
        }
        return content;
    }

    getCurrentCard(): Card {
        if (this.dekkCards?.length > 0 && this.currentCardIndex > -1) {
            const card = this.dekkCards[this.currentCardIndex];
            if (!card.visited) {
                ++ this.totalCardsStudied;
            }
            card.visited = true;
            card.image_links = card.image_links ?? [];
            card.is_bookmarked = !!card.is_bookmarked; // setting this to false in case it is not set
            return card;
        }
        return CardUtils.getDummyCard();
    }

    markGotCardRight(): void {
        if (!this.dekkCards[this.currentCardIndex].rightWrongMarked) {
            ++ this.rightCards;
        }
        this.dekkCards[this.currentCardIndex].rightWrongMarked = true;
    }

    markCardAsRead(card: Card): void {
        const urlParams = card?.card_id ? '/' + card?.card_id : '';
        this.httpClientService.get(UrlConstants.VIEW_CARD + urlParams).subscribe(() => {});
    }

    bookmark(card: Card): void {
        const urlParams = card.card_id ? '/' + card.card_id : '';
        this.httpClientService.get(UrlConstants.BOOKMARK_CARD + urlParams).subscribe(() => {
            card.is_bookmarked = true;
        });
    }

    unbookmark(card: Card): void {
        const urlParams = card?.card_id ? '/' + card.card_id : '';
        this.httpClientService.get(UrlConstants.UNBOOKMARK_CARD + urlParams).subscribe(() => {
            card.is_bookmarked = false;
        });
    }
}