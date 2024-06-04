import { Component, OnInit, Input, AfterViewInit, ViewEncapsulation } from '@angular/core';
import * as L from 'leaflet';

@Component({
  selector: 'app-leaflet-map',
  templateUrl: './leaflet-map.component.html',
  styleUrls: ['./leaflet-map.component.css']
})
export class LeafletMapComponent implements OnInit, AfterViewInit {
  @Input() coordinates: string | undefined;
  @Input() establishmentName: string | undefined;
  @Input() mapId: string = '';

  private map: L.Map | undefined;

  constructor() { }

  ngOnInit(): void {}

  ngAfterViewInit(): void {
    this.initMap();
  }

  private initMap(): void {
    if (!this.coordinates) return;

    const [lat, lng] = this.coordinates.split(',').map(coord => parseFloat(coord.trim()));

    this.map = L.map(this.mapId, {
      center: [lat, lng],
      zoom: 14
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(this.map);

    L.marker([lat, lng]).addTo(this.map)
      .bindPopup(this.establishmentName || `Coordinates: ${lat}, ${lng}`)
      .openPopup();
  }
}
