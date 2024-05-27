import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';

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

  generateHTMLContent() {
    const nodes = this.graphData.nodes;
    const edges = this.graphData.links;
    const nodeMap = new Map();

    nodes.forEach((node: { id: any; }) => nodeMap.set(node.id, node));

    const rootNode = nodes.find((node: { id: any; }) => !edges.some((edge: { target: any; }) => edge.target === node.id));

    this.htmlContent = this.createHTMLElement(rootNode, nodeMap, edges);
  }

  createHTMLElement(node: { balise: any; text: any; id: any; }, nodeMap: Map<any, any>, edges: any[]): string {
    let element = `<${node.balise}>${node.text || ''}`;

    const children = edges.filter(edge => edge.source === node.id).map(edge => nodeMap.get(edge.target));

    children.forEach(child => {
      element += this.createHTMLElement(child, nodeMap, edges);
    });

    element += `</${node.balise}>`;
    return element;
  }
}
