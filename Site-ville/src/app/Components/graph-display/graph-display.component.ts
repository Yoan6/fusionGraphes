import { Component, OnInit } from '@angular/core';
import { GraphService } from 'src/app/Services/graph.service';

@Component({
  selector: 'app-graph-display',
  templateUrl: './graph-display.component.html',
  styleUrls: ['./graph-display.component.css']
})
export class GraphDisplayComponent implements OnInit {

  graphData: any;
  htmlContent: string = '';

  constructor(
    private graphService: GraphService
  ) { }

  ngOnInit(): void {
    this.graphService.getGraphData().subscribe(data => {
      this.graphData = data;
      this.generateHTMLContent();
    });
  }

  generateHTMLContent() {
    const nodes = this.graphData.nodes;
    const edges = this.graphData.links;
    const nodeMap = new Map();

    // Crée une map des nœuds
    // @ts-ignore
    nodes.forEach(node => nodeMap.set(node.id, node));

    // Trouver le nœud racine (sans parent)
    // @ts-ignore
    const rootNode = nodes.find(node => !edges.some(edge => edge.target === node.id));

    // Générer le contenu HTML de manière récursive
    this.htmlContent = this.createHTMLElement(rootNode, nodeMap, edges);
  }

  // @ts-ignore
  createHTMLElement(node, nodeMap, edges): string {
    let element = `<${node.balise}>${node.text || ''}`;

    // Trouver les enfants du nœud courant
    // @ts-ignore
    const children = edges.filter(edge => edge.source === node.id).map(edge => nodeMap.get(edge.target));

    // Ajouter les enfants de manière récursive
    // @ts-ignore
    children.forEach(child => {
      element += this.createHTMLElement(child, nodeMap, edges);
    });

    element += `</${node.balise}>`;
    return element;
  }

}
