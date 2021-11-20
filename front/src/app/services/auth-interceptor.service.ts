import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class AuthInterceptorService implements HttpInterceptor {

    constructor(private cookieService: CookieService) { }

    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        const csrf = this.cookieService.get('csrftoken');
        const session = this.cookieService.get('sessionid');
        let request
        if (csrf && session) {
            request = req.clone({
                headers: req.headers
                    .set('X-CSRFToken', csrf),
                withCredentials: true
            });
        }
        else {
            request = req.clone({
                withCredentials: true
            });
        }
        return next.handle(request);
    }
}
