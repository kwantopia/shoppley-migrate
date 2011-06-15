//
//  SLDataController.h
//  shoppleyClient
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import <Foundation/Foundation.h>


@interface SLDataController : NSObject {
    
}

@property (nonatomic, retain) NSString* errorString;

+ (SLDataController*)sharedInstance;

#pragma mark -
#pragma mark User
- (BOOL)authenticateEmail:(NSString*)email password:(NSString*)password;

@end
