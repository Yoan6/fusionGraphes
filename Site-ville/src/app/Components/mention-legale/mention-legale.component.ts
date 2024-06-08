import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from "@angular/router";

@Component({
  selector: 'app-mention-legale',
  templateUrl: './mention-legale.component.html',
  styleUrls: ['./mention-legale.component.css']
})
export class MentionLegaleComponent implements OnInit {
  cityWiki: string | null = '';

  constructor(
    private route: ActivatedRoute,
    ) {}

  ngOnInit() {
    this.cityWiki = this.route.snapshot.paramMap.get('cityWiki');
  }

  goBack() {
    window.history.back();
  }
}
