import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateDekkCardComponent } from './create-dekk-card.component';

describe('CreateDekkCardComponent', () => {
  let component: CreateDekkCardComponent;
  let fixture: ComponentFixture<CreateDekkCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateDekkCardComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateDekkCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
