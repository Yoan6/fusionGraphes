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

  ngOnChanges(changes: SimpleChanges) {
    if (changes['graphData'] && changes['graphData'].currentValue) {
      this.generateHTMLContent();
    }
  }

  ngAfterViewInit() {
    this.insertDynamicComponents();
  }

  generateHTMLContent() {
    if (!this.graphData) return;
    this.container.clear();
    this.htmlContent = this.createHTMLElementRecursive(this.graphData, '');
    this.elRef.nativeElement.querySelector('#staticContent').innerHTML = this.htmlContent;
  }

  createHTMLElementRecursive(element: any, currentTitle: string): string {
    if (!element) return '';

    const { balise, title, text, children } = element;
    let html = '';

    if (['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(balise)) {
      html += `<${balise}>${title}</${balise}>`;
      currentTitle = title; // Mettre à jour le titre courant
      if (children && Array.isArray(children)) {
        children.forEach((child: any) => {
          html += this.createHTMLElementRecursive(child, currentTitle);
        });
      }
    } else if (balise === 'p') {
      if (title === 'Coordonnées') {
        const uniqueId = 'map-' + Math.random().toString(36).substr(2, 9);
        html += `<div id="${uniqueId}" class="dynamic-map" data-coordinates="${text}" data-establishment-name="${currentTitle}"></div>`;
      } else {
        html += `<${balise}>${text}</${balise}>`;
      }
    } else if (balise === 'table') {
      html += `<${balise}>`;
      if (children && Array.isArray(children)) {
        children.forEach((child: any) => {
          if (child.balise === 'tr') {
            html += `<tr>${this.createHTMLElementRecursive(child, currentTitle)}</tr>`;
          }
        });
      }
      html += `</${balise}>`;
    } else if (balise === 'tr') {
      // Si le titre de la ligne est le site web, on ajoute un lien et on ajoute 'http://' devant l'URL
      if (title === 'Site web') {
        const url = 'http://' + text;
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

  insertDynamicComponents() {
    const placeholders = this.elRef.nativeElement.querySelectorAll('.dynamic-map');
    placeholders.forEach((placeholder: HTMLElement) => {
      const coordinates = placeholder.getAttribute('data-coordinates');
      const establishmentName = placeholder.getAttribute('data-establishment-name');
      const factory = this.resolver.resolveComponentFactory(LeafletMapComponent);
      const componentRef: ComponentRef<LeafletMapComponent> = this.container.createComponent(factory);
      componentRef.instance.coordinates = coordinates!;
      componentRef.instance.establishmentName = establishmentName!;
      componentRef.instance.mapId = placeholder.id;
      placeholder.appendChild(componentRef.location.nativeElement);
    });
    this.cdr.detectChanges(); // Trigger change detection manually
  }
}
