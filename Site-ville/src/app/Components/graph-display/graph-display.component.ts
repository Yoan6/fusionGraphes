import { Component, Input, OnChanges, SimpleChanges, ComponentFactoryResolver, ViewChild, ViewContainerRef, ComponentRef, ElementRef, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { LeafletMapComponent } from '../leaflet-map/leaflet-map.component';

@Component({
  selector: 'app-graph-display',
  templateUrl: './graph-display.component.html',
  styleUrls: ['./graph-display.component.css']
})
export class GraphDisplayComponent implements OnChanges, AfterViewInit {
  @Input() graphData: any;
  htmlContent: string = '';
  @ViewChild('dynamicContent', { read: ViewContainerRef, static: true }) container!: ViewContainerRef;

  constructor(private resolver: ComponentFactoryResolver, private elRef: ElementRef, private cdr: ChangeDetectorRef) {}

  // Détecte les changements dans les données d'entrée et génère le contenu HTML statique
  ngOnChanges(changes: SimpleChanges) {
    if (changes['graphData'] && changes['graphData'].currentValue) {
      this.generateHTMLContent();
    }
  }

  // Fonction appelée après l'initialisation des vues enfants pour insérer les composants dynamiques (cartes intéractives)
  ngAfterViewInit() {
    this.insertDynamicComponents();
  }

  // Générer le contenu HTML statique à partir des données du graphe
  generateHTMLContent() {
    if (!this.graphData) return;
    this.container.clear();   // Nettoie les composants dynamiques précédents
    this.htmlContent = this.createHTMLElementRecursive(this.graphData, '');   // Crée le contenu HTML
    this.elRef.nativeElement.querySelector('#staticContent').innerHTML = this.htmlContent;    // Insère le contenu HTML dans le template dans la balise #staticContent
  }

  // Fonction récursive pour créer le contenu HTML à partir des données du graphe
  createHTMLElementRecursive(element: any, currentTitle: string): string {
    if (!element) return '';

    const { balise, title, text, children } = element;
    let html = '';

    // Si la balise est un titre, on l'ajoute au contenu HTML et on continue la récursion sur les enfants
    if (['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(balise)) {
      html += `<${balise}>${title}</${balise}>`;
      currentTitle = title; // Mise à jour du titre courant
      if (children && Array.isArray(children)) {
        children.forEach((child: any) => {
          html += this.createHTMLElementRecursive(child, currentTitle);
        });
      }
    } else if (balise === 'p') {
      if (title === 'Coordonnées') {
        const uniqueId = 'map-' + Math.random().toString(36).substr(2, 9);
        html += `<div id="${uniqueId}" class="dynamic-map" data-coordinates="${text}" data-establishment-name="${currentTitle}"></div>`;
      }
      // On n'affiche pas la dernière mise à jour des élus ou de DATAtourisme dans le contenu statique
      else if (title == 'Dernière modif élus' || title == 'Dernière modif DATAtourisme') {
        html += ``;
      }
      else {
        html += `<${balise}>${text}</${balise}>`;
      }
    } else if (balise === 'table') {
      html += `<${balise}>`;
      // On ajoute le titre du tableau
      html += `<tr><th colspan="2">${title}</th></tr>`;
      if (children && Array.isArray(children)) {
        children.forEach((child: any) => {
          if (child.balise === 'tr') {
            html += `<tr>${this.createHTMLElementRecursive(child, currentTitle)}</tr>`;
          }
        });
      }
      html += `</${balise}>`;
    } else if (balise === 'tr') {
      if (title === 'Site web') {
        let url = text;
        // Si le titre de la ligne est le site web, on ajoute un lien et on ajoute 'https://' devant l'URL s'il n'y est pas déjà
        if (!text.startsWith('http://') && !text.startsWith('https://')) {
          url = 'https://' + text;
        }
        else {
          url = text;
        }
        html += `<td><bold>${title}</bold></td><td><a href="${url}" target="_blank">${text}</a></td>`;
      } else {
        html += `<td>${title}</td><td>${text}</td>`;
      }
    } else if (balise === 'ul') {
      html += `<${balise}>`;
      if (children && Array.isArray(children)) {
        children.forEach((child: any) => {
          if (child.balise === 'li') {
            html += `<li>${this.createHTMLElementRecursive(child, currentTitle)}</li>`;
          }
        });
      }
      html += `</${balise}>`;
    } else if (balise === 'li') {
      html += `${text || ''}`;
    }

    return html;
  }

  // Insère les composants dynamiques dans les placeholders pour les cartes
  insertDynamicComponents() {
    const placeholders = this.elRef.nativeElement.querySelectorAll('.dynamic-map');
    placeholders.forEach((placeholder: HTMLElement) => {
      const coordinates = placeholder.getAttribute('data-coordinates');
      const establishmentName = placeholder.getAttribute('data-establishment-name');
      const factory = this.resolver.resolveComponentFactory(LeafletMapComponent);   //
      const componentRef: ComponentRef<LeafletMapComponent> = this.container.createComponent(factory);
      componentRef.instance.coordinates = coordinates!;
      componentRef.instance.establishmentName = establishmentName!;
      componentRef.instance.mapId = placeholder.id;
      placeholder.appendChild(componentRef.location.nativeElement);
    });
    this.cdr.detectChanges(); // Trigger change detection manually
  }
}
