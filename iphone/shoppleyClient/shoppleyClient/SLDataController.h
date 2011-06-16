//
//  SLDataController.h
//  shoppleyClient
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>

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
@interface SLDataController : NSObject {
    NSArray* _currentOffers;
    SLDataDownloader* _currentOffersDownloader;
}

@property (nonatomic, retain) NSString* errorString;
@property (nonatomic, retain) NSArray* currentOffers;

+ (SLDataController*)sharedInstance;

#pragma mark -
#pragma mark User
- (BOOL)authenticateEmail:(NSString*)email password:(NSString*)password;

#pragma mark -
#pragma mark Offers

// Return nil, if the data is not downloaded. Caller should try again later.
- (NSArray*)obtainCurrentOffersWithDelegate:(id <SLDataDownloaderDelegate>)delegate forcedDownload:(BOOL)forcedDownload;
@end
