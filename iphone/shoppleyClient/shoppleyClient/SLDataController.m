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
        [request.parameters setValue:[NSNumber numberWithFloat:47.78799] forKey:@"lat"];
        [request.parameters setValue:[NSNumber numberWithFloat:98.9989] forKey:@"lon"];
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
    
    [_delegate didFinishDownload];
    _isDownloading = NO;
}

- (void)request:(TTURLRequest*)request didFailLoadWithError:(NSError*)error {
    TTDPRINT(@"DataDownloader Error: %@ - %@", error.localizedDescription, error.localizedFailureReason);
    [_delegate didFailDownload];
    _isDownloading = NO;
}

@end

#pragma mark -
#pragma mark SLDataController

@implementation SLDataController
@synthesize errorString = _errorString, currentOffers = _currentOffers, redeemedOffers = _redeemedOffers;

- (id) init {
	if ((self = [super init])) {
    
    }
	return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_errorString);
    TT_RELEASE_SAFELY(_currentOffers);
    TT_RELEASE_SAFELY(_redeemedOffers);
    TT_RELEASE_SAFELY(_currentOffersDownloader);
    TT_RELEASE_SAFELY(_redeemedOffersDownloader);
	[super dealloc];
}

+ (SLDataController*)sharedInstance {
	static SLDataController *instance = nil;
	if (instance == nil) {
        instance = [[SLDataController alloc] init];
    }
	return instance;
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

@end
