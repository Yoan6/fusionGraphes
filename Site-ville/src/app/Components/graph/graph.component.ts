import { Component, Input, OnInit, HostListener } from '@angular/core';
import { Router } from "@angular/router";

@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.css']
})
export class GraphComponent implements OnInit {
  graphData: any;
  cityWiki: string = '';
  lastUpdateDATAtourisme: string = '';
  lastUpdateElus: string = '';
  private lastScrollTop: number = 0;
  private showBanner: boolean = false;

  constructor(private router: Router) {}

  ngOnInit() {
    this.graphData = history.state.data;
    this.cityWiki = history.state.cityWiki;
    if (!this.graphData) {
      this.router.navigate(['/']);
    }
    this.setLastUpdate();
  }

  goBack() {
    this.router.navigate(['/']);
  }

  setLastUpdate() {
    if (!this.graphData) return;
    this.lastUpdateDATAtourisme = this.getLastUpdateDATAtourismeRecursive(this.graphData);
  }

  // Parcours récursif de l'arbre de données pour trouver la date de dernière mise à jour DATAtourisme
  getLastUpdateDATAtourismeRecursive(element: any): string {
    if (!element) return '';

    const { balise, title, text, children } = element;
    let lastUpdateDATAtourisme = '';
    const textDate = this.convertToDate(text);

    if (balise === 'p' && title === 'Dernière modif élus') {
      this.lastUpdateElus = text;
    } else if (balise === 'p' && title === 'Dernière modif DATAtourisme' && textDate && (!lastUpdateDATAtourisme || textDate > this.convertToDate(lastUpdateDATAtourisme)!)) {
      lastUpdateDATAtourisme = text;
    } else if (children && Array.isArray(children)) {
      children.forEach((child: any) => {
        const childLastUpdate = this.getLastUpdateDATAtourismeRecursive(child);
        if (childLastUpdate && (!lastUpdateDATAtourisme || this.convertToDate(childLastUpdate)! > this.convertToDate(lastUpdateDATAtourisme)!)) {
          lastUpdateDATAtourisme = childLastUpdate;
        }
      });
    }
    return lastUpdateDATAtourisme;
  }

  // Convertit une date au format 'dd-mm-yyyy' en objet Date
  convertToDate(dateStr: string): Date | null {
    if (!dateStr) return null;
    const parts = dateStr.split('-');
    if (parts.length !== 3) return null;
    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1;
    const year = parseInt(parts[2], 10);
    return new Date(year, month, day);
  }

  // Retourne en haut de la page
  scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  @HostListener('window:scroll', [])
  onScroll() {
    const st = window.pageYOffset || document.documentElement.scrollTop;
    if (st < this.lastScrollTop) {
      this.showBanner = true;
    } else {
      this.showBanner = false;
    }
    this.lastScrollTop = st <= 0 ? 0 : st; // For Mobile or negative scrolling
    this.toggleBanner();
  }

  // Montre ou cache le bandeau de retour en haut de page
  toggleBanner() {
    const banner = document.getElementById('backToTopBanner');
    if (banner) {
      // Si on est en bas de page, on affiche le bandeau
      if (this.showBanner && this.lastScrollTop > 0) {
        banner.classList.add('show');
      } else {
        banner.classList.remove('show');
      }
    }
  }
}
