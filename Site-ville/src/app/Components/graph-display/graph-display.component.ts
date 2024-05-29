import {Component, Input, OnChanges, SimpleChanges} from '@angular/core';

@Component({
  selector: 'app-graph-display',
  templateUrl: './graph-display.component.html',
  styleUrls: ['./graph-display.component.css']
})
export class GraphDisplayComponent implements OnChanges {

  @Input() graphData: any;
  htmlContent: string = '';

  ngOnChanges(changes: SimpleChanges) {
    if (changes['graphData'] && changes['graphData'].currentValue) {
      this.generateHTMLContent();
    }
  }

  // Génère le code HTML à partir des données du graphe
  generateHTMLContent() {
    if (!this.graphData) return;

    let element = this.graphData;

    this.htmlContent = this.createHTMLElementRecursive(element);
  }

  // Parcourt des éléments du graphe pour générer le code HTML en fonction des balises
  createHTMLElementRecursive(element: any) {
    let html = '';

    // Si il n'y a plus d'élément, on retourne le code HTML
    if (!element) return html;

    let balise = element.balise;
    let title = element.title;
    let text = element.text;
    let children = element.children;

    // Pour les titres on affiche le title et on parcourts les éléments fils et on appelle récusivement la fonction
    if (['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(balise)) {
      html += `<${balise}>${title}</${balise}>`;
      if (children && Array.isArray(children)) {
        children.forEach((child: any) => {
          html += this.createHTMLElementRecursive(child);
        });
      }
    }
    // Pour les paragraphes on affiche simplement le texte
    else if (balise === 'p') {
      html += `<${balise}>${text}</${balise}>`;
    }
    // Pour les tables on affiche le text et on parcourt les éléments fils et on appelle récusivement la fonction
    else if (balise === 'table') {
      html += `<${balise}>`;
      if (children && Array.isArray(children)) {
        children.forEach((child: any) => {
          if (child.balise === 'tr') {
            html += `<tr>${this.createHTMLElementRecursive(child)}</tr>`;
          }
        });
      }
      html += `</${balise}>`;
    }
    else if (balise === 'tr') {
      html += `<td>${title}</td><td>${text}</td>`;
    }
    // Pour les listes on affiche le text et on parcourt les éléments fils et on appelle récusivement la fonction
    else if (balise === 'ul') {
      html += `<${balise}>`;
      if (children && Array.isArray(children)) {
        children.forEach((child: any) => {
          if (child.balise === 'li') {
            html += `<li>${this.createHTMLElementRecursive(child)}</li>`;
          }
        });
      }
      html += `</${balise}>`;
    }
    // Pour les éléments de liste on affiche le texte s'il existe
    else if (balise === 'li') {
      html += `${text || ''}`;
    }
    return html;
  }
}
