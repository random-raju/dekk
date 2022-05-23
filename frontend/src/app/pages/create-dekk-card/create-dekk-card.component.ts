import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { UrlConstants } from 'src/app/common/constants/url.constants';
import { Dekk } from 'src/app/common/models/dekk';
import { HomeResponse } from 'src/app/common/models/home-response';
import { HttpClientService } from 'src/app/common/services/http-client.service';
import { DekkUtils } from 'src/app/common/utils/dekk-utils';
import { Tag } from 'src/app/common/models/tag';
import { TagsService } from 'src/app/common/services/tags.service';
import { MatDialog } from '@angular/material/dialog';
import { PopupConstants } from 'src/app/common/constants/popup.constants';
import { DekkService } from 'src/app/common/services/dekk-service';
import { MsgDialogComponent } from 'src/app/common/components/msg-dialog/msg-dialog.component';
import { ErrorDialogComponent } from 'src/app/common/components/error-dialog/error-dialog.component';
import { Router } from '@angular/router';

// import * as $ from 'jquery';

@Component({
  selector: 'app-create-dekk-card',
  templateUrl: './create-dekk-card.component.html',
  styleUrls: ['./create-dekk-card.component.scss']
})
export class CreateDekkCardComponent implements OnInit {

  isLoading: boolean = true;
  newDekkNameAddedIfApplicable: Dekk[] = [];
  dekks = new FormControl();
  tags = new FormControl();
  allDekkOptions: Dekk[];
  dekkOptions: Dekk[];
  allTagOptions: Tag[];
  tagOptions: Tag[];
  selectedDekk: Dekk = DekkUtils.getEmptyDekk();
  newLabelPlaceholder: string = ''
  cardName: string = '';
  currentCardId: string;
  frontContent: string;
  backContent: string;

  // latestHighlight: any;
  // latestHighlightedField: any;

  dekkLoadListener: any;

  constructor(private httpClientService: HttpClientService, public tagsService: TagsService, private dialog: MatDialog, private dekkService: DekkService, private router: Router) { 
    this.isLoading = true;
    this.tagsService.loadTags().subscribe(()=>{
      this.allTagOptions = tagsService.tagsList;
      this.tagOptions = this.allTagOptions;
    });
    this.dekkLoadListener = this.httpClientService.get(UrlConstants.HOME_URL, []).subscribe((response: HomeResponse) => {
      const personalDekkList = response && response.user_dekks ? response.user_dekks : [];
      this.dekks.setValue(personalDekkList);
      this.allDekkOptions = personalDekkList;
      this.dekkOptions = this.allDekkOptions;
      this.isLoading = false;
    });

    // document.onmouseup = document.onkeyup = document.onselectionchange = () => {
    //   console.log(window.getSelection()?.toString());
    //   this.latestHighlight = window.getSelection();
    //   setTimeout(() => {
    //     this.latestHighlightedField = document.activeElement?.id === 'front-content' ? 'front' : (document.activeElement?.id === 'back-content' ? 'back' : null);
    //   }, 250);
    // };
  }

  ngOnInit(): void { }

  filterDekk($event: any) {
    if ($event === '') {
      this.dekkOptions = this.allDekkOptions;
    } else {
      const shortlistedDekkOptions = this.allDekkOptions.filter((dekk: Dekk) => dekk.tag_name.toLowerCase().startsWith($event.toLowerCase()));
      this.dekkOptions = shortlistedDekkOptions.filter((dekk: Dekk) => dekk.tag_name.toLowerCase().trim() === $event.toLowerCase().trim()).length === 0 ? [ {tag_name: $event.toLowerCase().trim()} as Dekk ].concat(shortlistedDekkOptions) : shortlistedDekkOptions;
    }
  }

  onDekkSelected($event: any): void {
    if (this.allDekkOptions.indexOf(this.dekks.value) < 0) { // ie new dekk
      this.allDekkOptions.push(this.dekks.value);

      // temp tracking of new dekk names in newDekkNameAddedIfApplicable array
      // not all these would be sent to backend to create new dekk
      // only the entry matching selectedDekk would be sent to backend to create new dekk
      this.newDekkNameAddedIfApplicable.push(this.dekks.value);
    }
    this.selectedDekk = this.dekks.value;

    if (this.newDekkNameAddedIfApplicable.indexOf(this.selectedDekk) >= 0) {
      this.newLabelPlaceholder = 'New ';
    } else {
      this.newLabelPlaceholder = '';
    }
  }

  filterTags($event: any) {
    console.log($event);
    if ($event === '') {
      this.tagOptions = this.allTagOptions;
    } else {
      const shortlistedTagOptions = this.allTagOptions.filter((tag: Tag) => tag.tag_name.toLowerCase().startsWith($event.toLowerCase()));
      this.tagOptions = shortlistedTagOptions.filter((tag: Tag) => tag.tag_name.toLowerCase().trim() === $event.toLowerCase().trim()).length === 0 ? [{
        tag_name: $event
      } as Tag].concat(shortlistedTagOptions) : shortlistedTagOptions;
      // this.tagOptions = shortlistedTagOptions;
    }
  }

  onTagSelected($event: any): void {
    if (!this.tags.value[0].tag_id) { // ie new tag
      this.allTagOptions.push(this.tags.value[0]);
    }
  }

  removeTag(tag: Tag): void {
    if (tag.tag_id) {
      this.tags.setValue(this.tags.value.filter((eachTag: Tag) => tag.tag_id !== eachTag.tag_id));
    } else {
      this.tags.setValue(this.tags.value.filter((eachTag: Tag) => tag.tag_name !== eachTag.tag_name));
    }
  }

  saveCard(): void {
    if (this.cardName?.length === 0) {
      this.cardSaveMsgPopup(PopupConstants.CARD_TITLE_ERROR);
      return;
    }

    // TODO - fix for highlights
    // if (!this.cardFrontEditComponent.convertCardContentToPayload()
    //   || !this.cardBackEditComponent.convertCardContentToPayload()) {
    //   this.cardSaveMsgPopup(PopupConstants.CARD_CONTENT_ERROR);
    //   return;
    // }

    if (!this.frontContent
      || !this.backContent) {
      this.cardSaveMsgPopup(PopupConstants.CARD_CONTENT_ERROR);
      return;
    }

    this.isLoading = true;
    const new_tags = this.tags && Object.keys(this.tags.value).length > 0 ? this.tags.value.filter((tag: any) => !tag.tag_id).map((tag: any) => tag.tag_name) : [];
    const selected_tag_ids = this.tags && Object.keys(this.tags.value).length > 0 ? this.tags.value.filter((tag: any) => !!tag.tag_id).map((tag: any) => tag.tag_id) : [];

    // Dekk creation case
    if (this.newLabelPlaceholder !== '') {
      this.isLoading = true;
      this.dekkService.saveDekkMetadata(this.selectedDekk.tag_name, '').subscribe((responseDekk: any) => {
        this.dekkService.saveCard({
          title: this.cardName,
          content_on_front: this.frontContent, //TODO this.cardFrontEditComponent.convertCardContentToPayload(),
          content_on_back: this.backContent, //TODO - this.cardBackEditComponent.convertCardContentToPayload(),
          dekk_id: responseDekk?.dekk_id,
          new_tags,
          selected_tag_ids
        }, this.currentCardId ?? '').subscribe((response: any) => {
          if (new_tags.length > 0) {
            this.tagsService.refreshTags();
          }
          this.router.navigate([UrlConstants.DEKK_EDIT_VIEW], {queryParams: { id: responseDekk?.dekk_id }});
        }, (error: any) => {
          this.handleCardSaveError();
        });
      }, (error: any) =>  {
        this.handleCardSaveError();
      });
    } else {
      this.dekkService.saveCard({
        title: this.cardName,
        content_on_front: this.frontContent, //TODO this.cardFrontEditComponent.convertCardContentToPayload(),
        content_on_back: this.backContent, //TODO - this.cardBackEditComponent.convertCardContentToPayload(),
        dekk_id: this.selectedDekk.tag_id,
        new_tags,
        selected_tag_ids
      }, this.currentCardId ?? '').subscribe((response: any) => {
        if (new_tags.length > 0) {
          this.tagsService.refreshTags();
        }
        this.router.navigate([UrlConstants.DEKK_EDIT_VIEW], {queryParams: { id: this.selectedDekk.tag_id }});
      }, (error: any) => {
        this.handleCardSaveError();
      });
    }
  }

  cardSaveMsgPopup(msg: string): void {
    const dialogRef = this.dialog.open(MsgDialogComponent, {
      data: {
          msg: msg
      }
    });
    dialogRef.afterClosed().subscribe(result => {
        console.log('The dialog was closed: ', result);
    });
  }

  handleCardSaveError(): void {
    const dialogRef = this.dialog.open(ErrorDialogComponent, {
      data: {
          msg: PopupConstants.CARD_METADATA_SAVE_ERROR
      }
    });
    dialogRef.afterClosed().subscribe(result => {
        console.log('The dialog was closed: ', result);
    });
  }

  testHighlight(): void {
    // console.log(this.latestHighlight + ' in ' + this.latestHighlightedField);
    // $('#testInput').focus();
    // $('#testInput').select();
  }
}
