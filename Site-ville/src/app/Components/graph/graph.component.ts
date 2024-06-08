import {Component, Input, OnInit} from '@angular/core';
import {Router} from "@angular/router";

@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.css']
})
export class GraphComponent implements OnInit {
  graphData: any;
  cityWiki: string = '';    // Permet d'avoir la ville avec le département pour les homonymes (Wikipédia) (sert pour la mention légale)

  constructor(private router: Router) {}

  ngOnInit() {
    this.graphData = history.state.data;
    this.cityWiki = history.state.cityWiki;
    if (!this.graphData) {
      this.router.navigate(['/']);
    }
  }

  goBack() {
    this.router.navigate(['/']);
  }
}
