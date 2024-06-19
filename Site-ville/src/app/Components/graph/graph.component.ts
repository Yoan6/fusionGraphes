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
  lastUpdateDATAtourisme: string = '';
  lastUpdateElus: string = '';

  constructor(private router: Router) {}

  ngOnInit() {
    this.graphData = history.state.data;
    console.log('Graph data', this.graphData);
    this.cityWiki = history.state.cityWiki;
    if (!this.graphData) {
      this.router.navigate(['/']);
    }
    this.setLastUpdate();
  }

  goBack() {
    this.router.navigate(['/']);
  }

  // Fonction pour récupérer la date de la dernière mise à jour du graphe pour les élus et les données DATAtourisme
  setLastUpdate() {
    if (!this.graphData) return;
    this.lastUpdateDATAtourisme = this.getLastUpdateDATAtourismeRecursive(this.graphData);
  }

  // Fonction récursive pour récupérer la date de la dernière mise à jour du graphe
  getLastUpdateDATAtourismeRecursive(element: any): string {
    if (!element) return '';

    const { balise, title, text, children } = element;
    let lastUpdateDATAtourisme = '';

    // Convertir le texte en objet Date si le texte représente une date
    const textDate = this.convertToDate(text);

    // Si la balise est la dernière mise à jour des élus, on la récupère
    if (balise === 'p' && title === 'Dernière modif élus') {
      this.lastUpdateElus = text;
    }
    // Si la balise est un paragraphe, que le titre est 'Dernière modif DATAtourisme' et que la date est plus récente que la plus récente actuelle, on récupère le texte
    else if (balise === 'p' && title === 'Dernière modif DATAtourisme' && textDate && (!lastUpdateDATAtourisme || textDate > this.convertToDate(lastUpdateDATAtourisme)!)) {
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

// Fonction pour convertir une chaîne de caractères en objet Date
  convertToDate(dateStr: string): Date | null {
    if (!dateStr) return null;

    const parts = dateStr.split('-');

    // Si la date n'est pas au format 'jj-mm-aaaa', on retourne null
    if (parts.length !== 3) return null;

    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1; // Les mois en JavaScript sont basés sur 0 (janvier est 0)
    const year = parseInt(parts[2], 10);

    return new Date(year, month, day);
  }
}
