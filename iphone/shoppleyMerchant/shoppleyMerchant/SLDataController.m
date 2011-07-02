//
//  SLDataController.m
//  shoppleyMerchant
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLDataController.h"

#import "extThree20JSON/extThree20JSON.h"
#import "extThree20JSON/JSON.h"
#import "SLActiveOffer.h"
#import "SLPastOffer.h"

//static NSString* kSLURLPrefix = @"http://www.shoppley.com/m/";
//static NSString* kSLURLPrefix = @"http://webuy-dev.mit.edu/m/";
static NSString* kSLURLPrefix = @"http://127.0.0.1:8000/m/";

#pragma mark -
#pragma mark SLDataDownloader

@implementation SLDataDownloader

- (id)initWithDataType:(NSString*)dataType delegate:(id <SLDataDownloaderDelegate>)delegate {
    if ((self = [self init])) {
        _dataType = [dataType copy];
        _delegate = delegate;
        _isDownloading = NO;
    }
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_dataType);
    [super dealloc];
}

- (void)download {
    @synchronized(self) {
        if (_isDownloading) return;
        _isDownloading = YES;
    }
    
    NSDictionary* endPoints = [NSDictionary dictionaryWithObjectsAndKeys:
                             @"merchant/offers/active/", @"active_offers",
                             @"merchant/offers/past/0/", @"past_offers",
                             nil];
    
    NSString* url = [kSLURLPrefix stringByAppendingString:[endPoints objectForKey:_dataType]];
    TTURLRequest* request = [TTURLRequest requestWithURL:url delegate:self];
    request.response = [[[TTURLJSONResponse alloc] init] autorelease];
    request.httpMethod = @"GET";
    
    request.cachePolicy = TTURLRequestCachePolicyNone;
    
    TTDPRINT(@"%@", url);
    TTDPRINT(@"%@", request.parameters);
    [request send];
}

- (void)requestDidFinishLoad:(TTURLRequest*)request {
    TTURLJSONResponse* jsonResponse = request.response;
    
    if (![jsonResponse.rootObject isKindOfClass:[NSDictionary class]]) {
        TTDPRINT(@"Server Error");
        return;
    }
    
    NSDictionary* response = jsonResponse.rootObject;
    TTDPRINT(@"%@",response);
    
    if ([request.urlPath rangeOfString:@"/active/"].location != NSNotFound) {
        [[SLDataController sharedInstance] setActiveOffers:[SLActiveOffer offersArrayfromDictionary:response]];
    } else if ([request.urlPath rangeOfString:@"/past/"].location != NSNotFound) {
        [[SLDataController sharedInstance] setPastOffers:[SLPastOffer offersArrayfromDictionary:response]];
    } else {
        TTDPRINT(@"Unrecognized request.");
    }
    
    if (_delegate) {
        [_delegate didFinishDownload];
    }
    _isDownloading = NO;
}

- (void)request:(TTURLRequest*)request didFailLoadWithError:(NSError*)error {
    TTDPRINT(@"DataDownloader Error: %@ - %@", error.localizedDescription, error.localizedFailureReason);
    if (_delegate) {
        [_delegate didFailDownload];
    }
    _isDownloading = NO;
}

@end

#pragma mark -
#pragma mark SLDataController

@implementation SLDataController
@synthesize errorString = _errorString, activeOffers = _activeOffers, pastOffers = _pastOffers, latitude = _latitude, longitude = _longitude;

+ (SLDataController*)sharedInstance {
	static SLDataController *instance = nil;
	if (instance == nil) {
        instance = [[SLDataController alloc] init];
    }
	return instance;
}

- (id)init {
	if ((self = [super init])) {
        _latitude = @"";
        _longitude = @"";
    }
	return self;
}

- (void)dealloc {
    [self clean];
    TT_RELEASE_SAFELY(_latitude);
    TT_RELEASE_SAFELY(_longitude);
    TT_RELEASE_SAFELY(_locationManager);
	[super dealloc];
}

- (void)clean {
    TT_RELEASE_SAFELY(_activeOffers);
    TT_RELEASE_SAFELY(_pastOffers);
    TT_RELEASE_SAFELY(_activeOffersDownloader);
    TT_RELEASE_SAFELY(_pastOffersDownloader);
}

- (void)reloadData {
    //[self updateLocation];
    TT_RELEASE_SAFELY(_activeOffers);
    TT_RELEASE_SAFELY(_pastOffers);
    [_activeOffersDownloader download];
    [_pastOffersDownloader download];
}

- (void)updateLocation {
    _isLocationReady = NO;
    
    _locationManager = [[CLLocationManager alloc] init];
    _locationManager.delegate = self;
    _locationManager.desiredAccuracy = kCLLocationAccuracyBest;
    [_locationManager startUpdatingLocation];
}

- (BOOL)sendPostRequestWithParameters:(NSDictionary*)parameters endpoint:(NSString*)endpoint {
    TTURLRequest* request = [TTURLRequest requestWithURL:[kSLURLPrefix stringByAppendingString:endpoint] delegate:self];
    request.response = [[[TTURLJSONResponse alloc] init] autorelease];
    [request.parameters setDictionary:parameters];
    request.httpMethod = @"POST";
    request.cachePolicy = TTURLRequestCachePolicyNone;
    
    TTDPRINT(@"%@", request.parameters);
    [request sendSynchronously];
    
    TTURLJSONResponse* jsonResponse = request.response;
    
    if ([jsonResponse.rootObject isKindOfClass:[NSDictionary class]]) {
        NSDictionary* response = jsonResponse.rootObject;
        if ([[response valueForKey:@"result"] intValue] >= 0) {
            return YES;            
        }
        _errorString = [response valueForKey:@"result_msg"];
        return NO;
    }
    _errorString = @"Connection Error. Please try again later.";
    return NO;
}

- (NSDictionary*)sendGetRequestWithParameters:(NSDictionary*)parameters endpoint:(NSString*)endpoint {
    TTURLRequest* request = [TTURLRequest requestWithURL:[kSLURLPrefix stringByAppendingString:endpoint] delegate:self];
    request.response = [[[TTURLJSONResponse alloc] init] autorelease];
    [request.parameters setDictionary:parameters];
    request.httpMethod = @"GET";
    request.cachePolicy = TTURLRequestCachePolicyNone;
    
    TTDPRINT(@"%@", request.parameters);
    [request sendSynchronously];
    
    TTURLJSONResponse* jsonResponse = request.response;
    
    if ([jsonResponse.rootObject isKindOfClass:[NSDictionary class]]) {
        NSDictionary* response = jsonResponse.rootObject;
        if ([[response valueForKey:@"result"] intValue]== 1) {
            return response;            
        }
        _errorString = [response valueForKey:@"result_msg"];
        return response;
    }
    _errorString = @"Connection Error. Please try again later.";
    return NULL;
}

#pragma mark -
#pragma mark User
- (BOOL)authenticateEmail:(NSString*)email password:(NSString*)password {
    TTURLRequest* request = [TTURLRequest requestWithURL:[kSLURLPrefix stringByAppendingString:@"login/"] delegate:self];
    request.response = [[[TTURLJSONResponse alloc] init] autorelease];
    [request.parameters setValue:email forKey:@"email"];
    [request.parameters setValue:password forKey:@"password"];
    request.httpMethod = @"POST";
    request.cachePolicy = TTURLRequestCachePolicyNone;
    [request sendSynchronously];
    
    TTURLJSONResponse* jsonResponse = request.response;
    
    if ([jsonResponse.rootObject isKindOfClass:[NSDictionary class]]) {
        NSDictionary* response = jsonResponse.rootObject;
        if ([[response valueForKey:@"result"] intValue]== 1) {
            // Persist username/password
            NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
            [defaults setObject:email forKey:@"email"];
            [defaults setObject:password forKey:@"password"];
            [defaults synchronize];
            
            return YES;            
        }
        _errorString = [response valueForKey:@"result_msg"];
        return NO;
    }
    _errorString = @"Connection Error. Please try again later.";
    return NO;
}

- (BOOL)_logout {
    TTURLRequest* request = [TTURLRequest requestWithURL:[kSLURLPrefix stringByAppendingString:@"logout/"] delegate:self];
    request.response = [[[TTURLJSONResponse alloc] init] autorelease];
    request.httpMethod = @"POST";
    request.cachePolicy = TTURLRequestCachePolicyNone;
    [request sendSynchronously];
    
    TTURLJSONResponse* jsonResponse = request.response;
    
    if ([jsonResponse.rootObject isKindOfClass:[NSDictionary class]]) {
        NSDictionary* response = jsonResponse.rootObject;
        if ([[response valueForKey:@"result"] intValue]== 1) {
            // Remove password
            NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
            [defaults removeObjectForKey:@"password"];
            [defaults synchronize];
            
            [self clean];
            return YES;            
        }
        _errorString = [response valueForKey:@"result_msg"];
        return NO;
    }
    _errorString = @"Connection Error. Please try again later.";
    return NO;
}

- (void)logout {
    [self _logout];
    [[TTNavigator navigator] removeAllViewControllers];
    [[TTNavigator navigator] openURLAction:[[TTURLAction actionWithURLPath:@"shoppley://login"] applyAnimated:NO]];
}

#pragma mark -
#pragma mark Offers
- (NSArray*)obtainActiveOffersWithDelegate:(id <SLDataDownloaderDelegate>)delegate forcedDownload:(BOOL)forcedDownload {
    if (forcedDownload || (_activeOffers == nil)) {
        if (!_activeOffersDownloader) {
            _activeOffersDownloader = [[SLDataDownloader alloc] initWithDataType:@"active_offers" delegate:delegate];
        }
        [_activeOffersDownloader download];
        return nil;
    } else {
        return _activeOffers;
    }
}

- (NSArray*)obtainPastOffersWithDelegate:(id <SLDataDownloaderDelegate>)delegate forcedDownload:(BOOL)forcedDownload {
    if (forcedDownload || (_pastOffers == nil)) {
        if (!_pastOffersDownloader) {
            _pastOffersDownloader = [[SLDataDownloader alloc] initWithDataType:@"past_offers" delegate:delegate];
        }
        [_pastOffersDownloader download];
        return nil;
    } else {
        return _pastOffers;
    }
}

#pragma mark -
#pragma mark Offer

- (NSDictionary*)sendMoreWithOfferId:(NSNumber*)offerId {
    return [self sendGetRequestWithParameters:[NSDictionary dictionaryWithObjectsAndKeys:nil] endpoint:[NSString stringWithFormat:@"merchant/offer/send/more/%@/", offerId]];
}

- (BOOL)redeemCode:(NSString*)code amount:(NSNumber*)amount {
    NSMutableDictionary* parameters = [[[NSMutableDictionary alloc] init] autorelease];
    [parameters setValue:amount forKey:@"amount"];
    [parameters setValue:code forKey:@"code"];
    return [self sendPostRequestWithParameters:parameters endpoint:@"merchant/offer/redeem/"];
}

- (BOOL)createNewOffer:(SLNewOffer*)offer {
    NSMutableDictionary* parameters = [[[NSMutableDictionary alloc] init] autorelease];
    [parameters setValue:offer.name forKey:@"title"];
    [parameters setValue:offer.description forKey:@"description"];
    [parameters setValue:offer.duration forKey:@"duration"];
    [parameters setValue:offer.unit forKey:@"units"];
    [parameters setValue:offer.amount forKey:@"amount"];
    
    if (offer.startTime) {
        NSDateFormatter* d = [[[NSDateFormatter alloc] init] autorelease];
        [d setDateFormat:@"YYYY-MM-dd"];
        NSString* date = [d stringFromDate:offer.startTime];
        
        NSDateFormatter* f = [[[NSDateFormatter alloc] init] autorelease];
        [f setDateFormat:@"hh:mm:ss a"];
        NSString* time = [f stringFromDate:offer.startTime];
        
        [parameters setValue:date forKey:@"date"];
        [parameters setValue:time forKey:@"time"];
        [parameters setValue:[NSNumber numberWithBool:NO] forKey:@"now"];
    } else {
        [parameters setValue:[NSNumber numberWithBool:YES] forKey:@"now"];
    }
    return [self sendPostRequestWithParameters:parameters endpoint:@"merchant/offer/start/"];
}

#pragma mark -
#pragma mark CLLocationManagerDelegate

- (void)locationManager:(CLLocationManager *)manager didUpdateToLocation:(CLLocation *)newLocation fromLocation:(CLLocation *)oldLocation {
    [_locationManager stopUpdatingLocation];
    
	_latitude = [[NSString stringWithFormat:@"%f", [newLocation coordinate].latitude] retain];
    _longitude = [[NSString stringWithFormat:@"%f", [newLocation coordinate].longitude] retain];
    
    TTDPRINT(@"Location %@ %@", _latitude, _longitude);
    _isLocationReady = YES;
}

- (void)locationManager:(CLLocationManager *)manager didFailWithError:(NSError *)error {
	TTDPRINT(@"Update location failed");
    _isLocationReady = YES;
}


@end
