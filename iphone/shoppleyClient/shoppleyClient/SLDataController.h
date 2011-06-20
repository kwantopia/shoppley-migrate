//
//  SLDataController.h
//  shoppleyClient
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <CoreLocation/CoreLocation.h>

#pragma mark -
#pragma mark SLDataDownloader

@protocol SLDataDownloaderDelegate
- (void)didFinishDownload;
- (void)didFailDownload;
@end

@interface SLDataDownloader : NSObject <TTURLRequestDelegate> {
    NSString* _dataType;
    id <SLDataDownloaderDelegate> _delegate;
    BOOL _isDownloading;
}

- (id)initWithDataType:(NSString*)dataType delegate:(id <SLDataDownloaderDelegate>)delegate;
- (void)download;

@end

#pragma mark -
#pragma mark SLDataController
@interface SLDataController : NSObject <CLLocationManagerDelegate> {
    NSString* _errorString;
    NSArray* _currentOffers;
    NSArray* _redeemedOffers;
    SLDataDownloader* _currentOffersDownloader;
    SLDataDownloader* _redeemedOffersDownloader;
    
    // Location
    BOOL _isLocationReady;
    NSString* _latitude;
    NSString* _longitude;
    CLLocationManager* _locationManager;
}

@property (nonatomic, retain) NSString* errorString;
@property (nonatomic, retain) NSArray* currentOffers;
@property (nonatomic, retain) NSArray* redeemedOffers;
@property (nonatomic, retain) NSString* latitude;
@property (nonatomic, retain) NSString* longitude;


+ (SLDataController*)sharedInstance;

- (void)clean;
- (void)updateLocation;

#pragma mark -
#pragma mark User
- (BOOL)authenticateEmail:(NSString*)email password:(NSString*)password;
- (BOOL)logout;

#pragma mark -
#pragma mark Offers

// Return nil, if the data is not downloaded. Caller should try again later.
- (NSArray*)obtainCurrentOffersWithDelegate:(id <SLDataDownloaderDelegate>)delegate forcedDownload:(BOOL)forcedDownload;
- (NSArray*)obtainRedeemedOffersWithDelegate:(id <SLDataDownloaderDelegate>)delegate forcedDownload:(BOOL)forcedDownload;
@end
