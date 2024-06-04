import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { GraphDisplayComponent } from './Components/graph-display/graph-display.component';
import { FormsModule } from "@angular/forms";
import { HttpClientModule } from "@angular/common/http";
import { LeafletMapComponent } from './Components/leaflet-map/leaflet-map.component';

@NgModule({
  declarations: [
    AppComponent,
    GraphDisplayComponent,
    LeafletMapComponent
  ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        FormsModule,
        HttpClientModule,
    ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
