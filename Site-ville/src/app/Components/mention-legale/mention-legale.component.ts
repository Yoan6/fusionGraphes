import {Component, OnInit} from '@angular/core';
import {ActivatedRoute} from "@angular/router";

@Component({
  selector: 'app-mention-legale',
  templateUrl: './mention-legale.component.html',
  styleUrls: ['./mention-legale.component.css']
})
export class MentionLegaleComponent implements OnInit {
  cityWiki: string | null = '';
  lastUpdateDATAtourisme: string | null = '';
  lastUpdateElus: string | null = '';

  constructor(
    private route: ActivatedRoute,
    ) {}

  ngOnInit() {
    this.cityWiki = this.route.snapshot.paramMap.get('cityWiki');
    this.lastUpdateDATAtourisme = this.route.snapshot.paramMap.get('lastUpdateDATAtourisme');
    this.lastUpdateElus = this.route.snapshot.paramMap.get('lastUpdateElus');
    // On transforme les tirets de la date en slashs pour l'affichage
    // @ts-ignore
    this.lastUpdateDATAtourisme = this.lastUpdateDATAtourisme?.replace(/-/g, '/');
  }

  goBack() {
    window.history.back();
  }
}
