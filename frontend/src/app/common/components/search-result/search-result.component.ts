import { Component, Input, OnChanges, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Card } from '../../models/card';
import { StudyService } from '../../services/study.service';

import * as _ from 'lodash';

@Component({
  selector: 'app-search-result',
  templateUrl: './search-result.component.html',
  styleUrls: ['./search-result.component.scss']
})
export class SearchResultComponent implements OnInit, OnChanges {

  @Input()
  card: any;

  constructor(public studyService: StudyService, private router: Router) { }

  ngOnInit(): void { }

  // TODO: fix dekk name and tags logic. not getting any tags??
  // TODO: highlighted content also not coming back. do highlight logic
  ngOnChanges() {
    // this.card.dekk_name = this.getTags()
    //   .filter((tag: string) => { return this.card.tags[tag] === 1 })
    //   .join(', ');
    this.card.dekk_name = 'Placeholder Dekk Name';
  }

  getTags(): string[] {
    // return _.keys(this.card.tags);
    return ['Placeholder tag 1', 'Placeholder tag 2'];
  }

  openCard(): void {
    // this.studyService.card = this.card;
    // this.router.navigate(['/card-view-details']);
  }

}
