//
//  SLDataController.m
//  shoppleyClient
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SLDataController.h"

#import "extThree20JSON/extThree20JSON.h"
#import "SLCurrentOffer.h"
#import "SLRedeemedOffer.h"

static NSString* kSLURLPrefix = @"http://webuy-dev.mit.edu/m/";
//static NSString* kSLURLPrefix = @"http://127.0.0.1:8000/m/";

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
                             @"customer/offers/current/", @"current_offers",
                             @"customer/offers/redeemed/", @"redeemed_offers",
                             nil];
    
    NSString* url = [kSLURLPrefix stringByAppendingString:[endPoints objectForKey:_dataType]];
    TTURLRequest* request = [TTURLRequest requestWithURL:url delegate:self];
    request.response = [[[TTURLJSONResponse alloc] init] autorelease];
    
    //AppDelegate *appDelegate = (AppDelegate *)[[UIApplication sharedApplication] delegate];
    //[request.parameters setValue:appDelegate.latitude forKey:@"lat"];
    //[request.parameters setValue:appDelegate.longitude forKey:@"lon"];
    
    if ([_dataType isEqualToString:@"current_offers"]) {
        [request.parameters setValue:[[SLDataController sharedInstance] latitude] forKey:@"lat"];
        [request.parameters setValue:[[SLDataController sharedInstance] longitude] forKey:@"lon"];
        request.httpMethod = @"POST";
    } else if ([_dataType isEqualToString:@"redeemed_offers"]) {
        request.httpMethod = @"GET";
    } else {
        TTDERROR(@"Unknown datatype");
    }
    
    request.cachePolicy = TTURLRequestCachePolicyNone;
    
    TTDPRINT(@"%@",request.parameters);
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
    
    if ([request.httpMethod isEqualToString:@"POST"]) {
        // current offers
        [[SLDataController sharedInstance] setCurrentOffers:[SLCurrentOffer offersArrayfromDictionary:response]];
    } else {
        [[SLDataController sharedInstance] setRedeemedOffers:[SLRedeemedOffer offersArrayfromDictionary:response]];
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
@synthesize errorString = _errorString, currentOffers = _currentOffers, redeemedOffers = _redeemedOffers, latitude = _latitude, longitude = _longitude;

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
    TT_RELEASE_SAFELY(_errorString);
    TT_RELEASE_SAFELY(_currentOffers);
    TT_RELEASE_SAFELY(_redeemedOffers);
    TT_RELEASE_SAFELY(_currentOffersDownloader);
    TT_RELEASE_SAFELY(_redeemedOffersDownloader);
}

+ (SLDataController*)sharedInstance {
	static SLDataController *instance = nil;
	if (instance == nil) {
        instance = [[SLDataController alloc] init];
    }
	return instance;
}

- (void)updateLocation {
    _isLocationReady = NO;
    
    _locationManager = [[CLLocationManager alloc] init];
    _locationManager.delegate = self;
    _locationManager.desiredAccuracy = kCLLocationAccuracyBest;
    [_locationManager startUpdatingLocation];
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

- (BOOL)logout {
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

#pragma mark -
#pragma mark Offers
- (NSArray*)obtainCurrentOffersWithDelegate:(id <SLDataDownloaderDelegate>)delegate forcedDownload:(BOOL)forcedDownload {
    if (forcedDownload || (_currentOffers == nil)) {
        if (!_currentOffersDownloader) {
            _currentOffersDownloader = [[SLDataDownloader alloc] initWithDataType:@"current_offers" delegate:delegate];
        }
        [_currentOffersDownloader download];
        return nil;
    } else {
        return _currentOffers;
    }
}

- (NSArray*)obtainRedeemedOffersWithDelegate:(id <SLDataDownloaderDelegate>)delegate forcedDownload:(BOOL)forcedDownload {
    if (forcedDownload || (_redeemedOffers == nil)) {
        if (!_redeemedOffersDownloader) {
            _redeemedOffersDownloader = [[SLDataDownloader alloc] initWithDataType:@"redeemed_offers" delegate:delegate];
        }
        [_redeemedOffersDownloader download];
        return nil;
    } else {
        return _redeemedOffers;
    }
}


#pragma mark -
#pragma mark CLLocationManagerDelegate

- (void)locationManager:(CLLocationManager *)manager didUpdateToLocation:(CLLocation *)newLocation fromLocation:(CLLocation *)oldLocation {
    [_locationManager stopUpdatingLocation];
    
	_latitude = [[NSString stringWithFormat:@"%f", [newLocation coordinate].latitude] retain];
    _longitude = [[NSString stringWithFormat:@"%f", [newLocation coordinate].longitude] retain];
    
    TTDPRINT(@"Location %@ %@", _latitude, _longitude);
    _isLocationReady = YES;
    
    [_currentOffersDownloader download];
}

- (void)locationManager:(CLLocationManager *)manager didFailWithError:(NSError *)error {
	TTDPRINT(@"Update location failed");
    _isLocationReady = YES;
}


@end
